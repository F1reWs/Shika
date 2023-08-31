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
from types import FunctionType
from typing import Union

from aiogram.types import CallbackQuery, InlineQuery, Message
from pyrogram import Client

from .. import database, types


class Item:
    """Элемент"""

    def __init__(self) -> None:
        """Инициализация класса"""
        self._all_modules: types.ModulesManager = None
        self._db: database.Database = None
        self._app: Client = None

    async def _check_filters(
        self,
        func: FunctionType,
        module: types.Module,
        update_type: Union[Message, InlineQuery, CallbackQuery],
    ) -> bool:
        """Проверка фильтров"""
        if (custom_filters := getattr(func, "_filters", None)):
            coro = custom_filters(module, self._app, update_type)
            if inspect.iscoroutine(coro):
                coro = await coro

            if not coro:
                return False
        else:
            if update_type.from_user.id != self._all_modules.me.id:
                return False

        return True
