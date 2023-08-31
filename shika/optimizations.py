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

import sys

def apply_optimizations() -> list:
    applied: list = []
    try:
        from uvloop import EventLoopPolicy
        from asyncio import set_event_loop_policy
        set_event_loop_policy(EventLoopPolicy())
        applied.append("uvloop")
    except ImportError:
        pass

    from . import json_provider
    sys.modules["json"] = json_provider.json
    if json_provider._jname != "json":
        applied.append(json_provider._jname)
    
    try:
        import re2
        import re

        # Переносим некотрые атрибуты из re в re2, так как их нету в re2
        re2_attr = dir(re2)
        missing = dir(re)
        for i in re2_attr:
            if i in missing:
                missing.remove(i)
        
        for item in missing:
            re_item = getattr(re, item)
            setattr(re2, item, re_item)

        sys.modules["re"] = re2
        applied.append("pyre2")
    except ImportError:
        pass

    try:
        import tgcrypto
        applied.append("tgcrypto")
    except ImportError:
        pass

    return applied