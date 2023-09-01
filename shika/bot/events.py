#     ______   __        _   __              
#   .' ____ \ [  |      (_) [  |  _          
#   | (___ \_| | |--.   __   | | / ]  ,--.   
#    _.____`.  | .-. | [  |  | '' <  `'_\ :  
#   | \____) | | | | |  | |  | |`\ \ // | |, 
#    \______.'[___]|__][___][__|  \_]\'-;__/ 

#    Shika (telegram userbot by https://github.com/F1reWs/Shika/graphs/contributors)
#    Copyright (C) 2023 Shika

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    GNU General Public License https://www.gnu.org/licenses.

import inspect
import logging

from aiogram.types import (CallbackQuery, InlineQuery,
                        InlineQueryResultArticle, InputTextMessageContent,
                        Message)

from .. import utils
from .types import Item, database


class Events(Item):
    """Обработчик событий"""

    def __init__(self):
        self.db = database.db

    async def _message_handler(self, message: Message) -> Message:
        """Обработчик сообщений"""
        for func in self._all_modules.message_handlers.values():
            if not await self._check_filters(func, func.__self__, message):
                continue

            try:
                await func(self._app, message)
            except Exception as error:
                logging.exception(error)

        return message

    async def _callback_handler(self, call: CallbackQuery) -> CallbackQuery:
        """Обработчик каллбек-хендлеров"""
        for func in self._all_modules.callback_handlers.values():
            if not await self._check_filters(func, func.__self__, call):
                continue

            try:
                await func(self._app, call)
            except Exception as error:
                logging.exception(error)

        return call

    async def _inline_handler(self, inline_query: InlineQuery) -> InlineQuery:
        """Обработчик инлайн-хендеров"""
        if not (query := inline_query.query):
            commands = ""
            ccommands = 0
            for command, func in self._all_modules.inline_handlers.items():
                if await self._check_filters(func, func.__self__, inline_query):
                    commands += f"\n💬 <code>@{(await self.bot.me).username} {command}</code>"
                    ccommands += 1
            if commands == "":
              message = InputTextMessageContent(
                         f"<b>😔 Нету доступных инлайн команд или у вас нет к ним доступа</b>"
                       )
              descr = f"У вас нет доступных команд"
            else:
              message = InputTextMessageContent(
                         f"<b>ℹ️ Доступные инлайн команды:</b>\n"
                         f"{commands}"
                       )
              descr = f"{ccommands} команд доступно"

            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title="Доступные инлайн команды",
                        description=descr,
                        input_message_content=message,
                        thumb_url="https://api.f1rew.me/file/speech_balloon_apple.png",
                    )
                ], cache_time=0
            )
        try:
          query_ = query.split()
          cmd = query_[0]
          args = " ".join(query_[1:])
        except IndexError:
          return

        func = self._all_modules.inline_handlers.get(cmd)
        if not func:
            return await inline_query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_id(),
                        title="Ошибка",
                        input_message_content=InputTextMessageContent(
                            "❌ <b>Инлайн команда не найдена!</b>"),
                        thumb_url="https://api.f1rew.me/file/x.png"
                    )
                ], cache_time=0
            )

        if not await self._check_filters(func, func.__self__, inline_query):
            return

        try:
            if (
                len(vars_ := inspect.getfullargspec(func).args) > 3
                and vars_[3] == "args"
            ):
                await func(self._app, inline_query, args)
            else:
                await func(self._app, inline_query)
        except Exception as error:
            logging.exception(error)

        return inline_query
