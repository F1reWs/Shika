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

"""Данный модуль выбирает лучший JSON-модуль из доступных и обеспечивает совместимость"""
from typing import Callable

try:
    import rapidjson as json
except ImportError:
    try:
        import ujson as json
    except ImportError:
        try:
            import simplejson as json
        except ImportError:
            import json

_jname: str = json.__name__.lower().strip()

if _jname != "json":
    import json as _json
    json_attr = dir(json)
    missing = dir(_json)
    for i in json_attr:
        if i in missing:
            missing.remove(i)
        
    for item in missing:
        json_item = getattr(_json, item)
        setattr(json, item, json_item)