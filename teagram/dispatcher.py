import logging
from inspect import getfullargspec, iscoroutine
from types import FunctionType

from pyrogram import Client, filters, types
from pyrogram.handlers import MessageHandler

from . import loader, utils


async def check_filters(func: FunctionType, app: Client, message: types.Message) -> bool:
    """Проверка фильтров"""
    if (custom_filters := getattr(func, "_filters", None)):
        coro = custom_filters(app, message)
        if iscoroutine(coro):
            coro = await coro

        if not coro:
            return False
    else:
        if not message.outgoing:
            return False

    return True


class DispatcherManager:
    """Менеджер диспетчера"""

    def __init__(self, app: Client, modules: "loader.ModulesManager") -> None:
        self.app = app
        self.modules = modules

    async def load(self) -> bool:
        """Загружает менеджер диспетчера"""
        logging.info("Загрузка диспетчера...")

        self.app.add_handler(
            MessageHandler(
                self._handle_message, filters.all)
        )

        logging.info("Диспетчер успешно загружен")
        return True

    async def _handle_message(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик сообщений"""
        await self._handle_watchers(app, message)
        await self._handle_other_handlers(app, message)

        prefix, command, args = utils.get_full_command(message)
        if not (command or args):
            return

        command = self.modules.aliases.get(command, command)
        func = self.modules.command_handlers.get(command.lower())
        if not func:
            return
    
        if not await check_filters(func, app, message):
            return

        try:
            if (
                len(vars_ := getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(app, message, utils.get_full_command(message)[2])
            else:
                await func(app, message)
        except Exception as error:
            logging.exception(error)
            await utils.answer(
                message, f"❌ Произошла ошибка при выполнении команды.\n"
                        f"Запрос был: <code>{message.text}</code>\n"
                        f"Подробности можно найти в <code>{prefix}logs</code>"
            )

        return message

    async def _handle_watchers(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик вотчеров"""
        for watcher in self.modules.watcher_handlers:
            try:
                if not await check_filters(watcher, app, message):
                    continue

                await watcher(app, message)
            except Exception as error:
                logging.exception(error)

        return message

    async def _handle_other_handlers(self, app: Client, message: types.Message) -> types.Message:
        """Обработчик других хендлеров"""
        for handler in app.dispatcher.groups[0]:
            if getattr(handler.callback, "__func__", None) == DispatcherManager._handle_message:
                continue

            coro = handler.filters(app, message)
            if iscoroutine(coro):
                coro = await coro

            if not coro:
                continue

            try:
                handler = handler.callback(app, message)
                if iscoroutine(handler):
                    await handler
            except Exception as error:
                logging.exception(error)

        return message
