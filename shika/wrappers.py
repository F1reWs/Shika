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

from asyncio import iscoroutine, wrap_future
from concurrent.futures import ThreadPoolExecutor
from functools import wraps as _wraps
from inspect import iscoroutinefunction
from types import ModuleType
from typing import Callable


def wrap_function_to_async(function: Callable) -> Callable:
    """Обворачивает синхронные функции в асинхронные"""

    # Некоторые проверки для безопасности
    assert (not iscoroutinefunction(function)), "Функция уже асинхронная!"
    assert (not iscoroutine(function)), "Ожидается функция, получена корутина."

    pool = ThreadPoolExecutor()

    @_wraps(function)
    def wrapped(*args, **kwargs):

        future = pool.submit(function, *args, **kwargs)
        return wrap_future(future)

    return wrapped


class WrapModuleToAsync:
    """Делает то же самое что и wrap_function_to_async но обворачивает уже целые модули"""

    def __init__(self, mod: ModuleType):
        for attr in dir(mod):
            item = getattr(mod, attr)

            # Проверяем полученный атрибут на асинхронность, если он не асинхронный, то обворачиваем
            if callable(item) and not iscoroutinefunction(item) and not iscoroutine(item):
                wrapped = wrap_function_to_async(item)
                setattr(self, attr, wrapped)
            else:
                setattr(self, attr, item)
