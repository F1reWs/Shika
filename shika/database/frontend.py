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

from typing import KT, VT, Union

from lightdb import LightDB
from pyrogram import Client, types

from . import CloudDatabase


class Database(LightDB):
    """Локальная база данных в файле"""

    def __init__(self, location: str):
        super().__init__(location)
        self.cloud = None

    def init_cloud(self, app: Client, me: types.User):
        """Инициализация облачной базы данных"""
        self.cloud = CloudDatabase(app, me)

    def __repr__(self):
        return object.__repr__(self)

    def set(self, name: str, key: KT, value: VT):
        self.setdefault(name, {})[key] = value
        return self.save()

    def get(self, name: str, key: KT, default: VT = None):
        try:
            return self[name][key]
        except KeyError:
            return default

    def pop(self, name: str, key: KT = None, default: VT = None):
        if not key:
            value = self.pop(name, default)
        else:
            try:
                value = self[name].pop(key, default)
            except KeyError:
                value = default

        self.save()
        return value

     async def save_data(self, message: Union[types.Message, str]):
         """Сохранить данные в чат"""
         return await self.cloud.save_data(message)

     async def get_data(self, message_id: int):
         """Найти данные по айди сообщения"""
         return await self.cloud.get_data(message_id)
