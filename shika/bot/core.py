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

import logging
import asyncio
import sys

from aiogram import Bot, Dispatcher, exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client

from typing import Union, NoReturn
from loguru import logger

from .events import Events
from .token_manager import TokenManager

from .. import database, __version__, types


class BotManager(
    Events,
    TokenManager
):
    """Менеджер бота"""

    def __init__(
        self,
        app: Client,
        db: database.Database,
        all_modules: types.ModulesManager
    ) -> None:
        """Инициализация класса

        Параметры:
            app (``pyrogram.Client``):
                Клиент

            db (``database.Database``):
                База данных

            all_modules (``loader.Modules``):
                Модули
        """
        self._app = app
        self._db = db
        self._all_modules = all_modules

        self._token = self._db.get("shika.bot", "token", None)

    async def load(self) -> Union[bool, NoReturn]:
        """Загружает менеджер бота"""
        logging.info("Загрузка менеджера бота...")
        error_text = "Юзерботу необходим бот. Реши проблему создания бота и запускай юзербот заново"

        not_set_token = False

        if not self._token:
            print("Токен не найден. Пересоздаем токен...")

            not_set_token = True

            token = await self._create_bot()
            self._token = token

            if self._token is False:
                logging.error(error_text)
                return sys.exit(1)

            self._db.set("shika.bot", "token", self._token)

        try:
            self.bot = Bot(self._token, parse_mode="html")
        except (exceptions.ValidationError, exceptions.Unauthorized):
            print("Токен не рабочий. Пересоздаем токен...")
         
            result = await self._revoke_token()

            if not result:
                self._token = await self._create_bot()
                if not self._token:
                    logging.error(error_text)
                    return sys.exit(1)

                self._db.set("shika.bot", "token", self._token)
                return await self.load()
            else:
                self._token = result
                self._db.set("shika.bot", "token", self._token)

                return await self.load()

        self._dp = Dispatcher(self.bot)

        self._dp.register_message_handler(
            self._message_handler, lambda _: True,
            content_types=["any"]
        )
        self._dp.register_inline_handler(
            self._inline_handler, lambda _: True
        )
        self._dp.register_callback_query_handler(
            self._callback_handler, lambda _: True
        )

        asyncio.ensure_future(
            self._dp.start_polling())

        self.bot.manager = self

        logger.success("Менеджер бота успешно загружен")

        me_info = await self._app.get_me()

        hello_text = f"""<b>
👋 Привет, {me_info.first_name}!

💻 Твой юзербот Shika установлен!

📔 Быстрый гайд

1️⃣ Напиши <code>.help</code> чтобы увидеть список модулей
2️⃣ Напиши <code>.help [название модуля]</code> чтобы увидеть информацию модуля
3️⃣ Напиши <code>.dlmod [ссылка]</code> чтобы загрузить модуль из ссылки
4️⃣ Напиши <code>.loadmod</code> ответом на файл, чтобы загрузить модуль из него
5️⃣ Напиши <code>.unloadmod [Название модуля]</code> чтобы выгрузить модуль
</b>
"""
        
        keyboard = InlineKeyboardMarkup(
     ).add(
        InlineKeyboardButton("🗞 Новости", url="https://t.me/shikaub"),
     ).add(
        InlineKeyboardButton("💬 Чат", url="https://t.me/shika_chat"),
        InlineKeyboardButton("🖥 Модули", url="https://t.me/shika_chat/12"),
     ).add(
        InlineKeyboardButton("🐈‍⬛ Github", url="https://github.com/F1reWs/Shika"),
     )

        if not_set_token == True:
            await self.bot.send_photo(chat_id=me_info.id, photo="https://global-uploads.webflow.com/6030eb20edb267a2d11d31f6/62ea266ac8026819f977ca7d_07UG_TelegramforBusiness_8bb65f395e5cea9300a99d7185d69afb_2000.png", caption=hello_text, parse_mode="HTML", reply_markup=keyboard)

        return True#
