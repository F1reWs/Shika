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

import time
import io
import os
import logging
from logging import StreamHandler

from pyrogram import Client, types

from .. import loader, utils


class CustomStreamHandler(StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs: list = []

    def emit(self, record):
        self.logs.append(record)

        super().emit(record)

handler = CustomStreamHandler()
log = logging.getLogger()
log.addHandler(handler)

@loader.module(name="Tester", author="shika")
class TesterMod(loader.Module):
    """Тест чего-то"""

    async def logs_cmd(self, app: Client, message: types.Message, args: str):
        app.me = await app.get_me()
        """Отправляет логи. Использование: logs <уровень>"""
        if not args:
            args = "40"

        try:
          lvl = int(args)
        except:
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji> Вы не указали уровень или указали неверный уровень логов</b>")

        if not args or lvl < 0 or lvl > 60:
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji> Вы не указали уровень или указали неверный уровень логов</b>")

        handler: CustomStreamHandler = log.handlers[1] # type: ignore
        logs = '\n'.join(str(error) for error in handler.logs).encode('utf-8')
        
        if not logs:
            return await utils.answer(
                message, f"<b><emoji id=5314302076317081739>❕</emoji> Нет логов на уровне {lvl} ({logging.getLevelName(lvl)})</b>")

        logs = io.BytesIO(logs)
        logs.name = "shika.log"

        await message.reply_document(
            document=logs,
            caption=f"<b><emoji id=5433614747381538714>📤</emoji> Shika Логи с {lvl} ({logging.getLevelName(lvl)}) уровнем</b>"
            )
        return await message.delete()
    
    async def setprefix_cmd(self, app: Client, message: types.Message, args: str):
        """Изменить префикс, можно несколько штук разделённые пробелом. Использование: setprefix <префикс> [префикс, ...]"""
        if not (args := args.split()):
            return await utils.answer(
                message, "<b><emoji id=6334850502722848701>❔</emoji> На какой префикс нужно изменить?</b>")

        self.db.set("shika.loader", "prefixes", list(set(args)))
        prefixes = ", ".join(f"<code>{prefix}</code>" for prefix in args)
        return await utils.answer(
            message, f"<b><emoji id=6334758581832779720>✅</emoji> Префикс был изменен на {prefixes}</b>")

    async def addalias_cmd(self, app: Client, message: types.Message, args: str):
        """Добавить алиас. Использование: addalias <новый алиас> <команда>"""
        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]
        if not (args := args.lower().split(maxsplit=1)):
            return await utils.answer(
                message, "<b><emoji id=6334850502722848701>❔</emoji> Какой алиас нужно добавить?</b>")

        if len(args) != 2:
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji> Неверно указаны аргументы.</b>"
                        f"<emoji id=6334758581832779720>✅</emoji><b> Правильно: <code>{prefix}addalias новый_алиас команда</code></b>"
            )

        aliases = self.all_modules.aliases
        if args[0] in aliases:
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji> Такой алиас уже существует</b>")

        if not self.all_modules.command_handlers.get(args[1]):
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji> Такой команды нет</b>")

        aliases[args[0]] = args[1]
        self.db.set("shika.loader", "aliases", aliases)

        return await utils.answer(
            message, f"<emoji id=6334758581832779720>✅</emoji><b> Алиас <code>{args[0]}</code> для команды <code>{args[1]}</code> был добавлен</b>")

    async def delalias_cmd(self, app: Client, message: types.Message, args: str):
        """Удалить алиас. Использование: delalias <алиас>"""
        if not (args := args.lower()):
            return await utils.answer(
                message, "<emoji id=6334850502722848701>❔</emoji><b> Какой алиас нужно удалить?</b>")

        aliases = self.all_modules.aliases
        if args not in aliases:
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji><b> Такого алиаса нет</b>")

        del aliases[args]
        self.db.set("shika.loader", "aliases", aliases)

        return await utils.answer(
            message, f"<emoji id=6334758581832779720>✅</emoji><b> Алиас <code>{args}</code> был удален</b>")

    async def aliases_cmd(self, app: Client, message: types.Message):
        """Показать все алиасы"""
        aliases = self.all_modules.aliases
        if not aliases:
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji><b>Алиасов нет</b>")

        return await utils.answer(
            message, "🗄 Список всех алиасов:\n" + "\n".join(
                f"• <code>{alias}</code> ➜ {command}"
                for alias, command in aliases.items()
            )
        )

    async def ping_cmd(self, app: Client, message: types.Message, args: str):
        """Команда для показание пинга"""
        start = time.perf_counter_ns()
        await utils.answer(message, "🌀")
        ping = round((time.perf_counter_ns() - start) / 10**6, 3)
        await utils.answer(
            message,
            f"""
<emoji id=5445284980978621387>🚀</emoji> **Время отлика Telegram:** `{ping}ms`
            """
        )

