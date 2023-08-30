import os
import sys
import time
import atexit
import asyncio

from pyrogram import Client, types
from .. import loader, utils
from ..types import Config, ConfigValue

<<<<<<< HEAD
=======
from .. import loader, utils, wrappers
from loguru import logger
from time import time

@wrappers.wrap_function_to_async
def create_backup(src: str, dest: str):
    name = f'backup_{round(time())}'
    exceptions = [name, 'backup', 'session', 'db', 'config', 'bot_avatar']
    
    zipp = os.path.join(dest, f'{name}.zip')
>>>>>>> 24a3a98478275cfeaf9fd661f2078ec17c679429

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

        await reply.download("." + str(self.db.location))

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
        

        
