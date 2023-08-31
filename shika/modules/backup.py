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

import os
import sys
import time
import atexit
import asyncio
import shutil

from pyrogram import Client, types
from .. import loader, utils
from ..types import Config, ConfigValue


@loader.module("Backuper", "shika")
class BackuperMod(loader.Module):
    """Создание бекапов базы данных"""
        
    def __init__(self):
        self.inline_bot = self.bot.bot

    async def backupdb_cmd(self, app: Client, message: types.Message):
        """Создать бекап всей базы данных. Использование: backupdb"""
        app.me = await app.get_me()
        if not os.path.exists(self.db.location):
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji>Ошибка! Файл с локальной базой данных не найден</b>")
        
        await app.send_document(
            chat_id="me",
            document=self.db.location,
            caption=f"<b><emoji id=5431736674147114227>🗂</emoji> Бекап базы данных</b>"
            )

        return await utils.answer(
            message, "<b><emoji id=6334758581832779720>✅</emoji> Бекап базы данных успешно создан и отправлен в избранное!</b>")

    async def restoredb_cmd(self, app: Client, message: types.Message):
        """Восстановить базу данных из файла с реплая. Использование: restoredb <реплай на файл с названием db.json>"""
        reply = message.reply_to_message
        if (
            not reply
            or not reply.document
            or reply.document.file_name != "db.json"
        ):
            return await message.edit("<b><emoji id=5312526098750252863>❌</emoji> Ошибка! Нет реплая на файл с названием db.json</b>")
        
        msg = await message.edit(f"<b><emoji id=5328274090262275771>🕐</emoji> Обновляем базу данных...</b>")
        
        down = await reply.download(str(self.db.location))
        shutil.copy2(down, "../db.json")
        
        await msg.edit(f"<b><emoji id=5774134533590880843>🔄</emoji> База данных обновлена!</b>")

        def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "shika")

        m = await message.reply(
text=f'<b><emoji id=5328274090262275771>🕐</emoji> Перезагрузка...</b>',)

        atexit.register(restart)
        self.db.set(
                "shika.loader", "restart", {
                    "msg": f"{m.chat.id}:{m.id}",
                    "start": str(round(time.time())),
                    "type": "restoredb"
                }
            )
        return sys.exit(0)
        

        
