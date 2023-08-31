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

try:
    import ujson as json
except ImportError:
    import json

from typing import Union

def save_db(
        api_id: Union[int, str], api_hash: str, token: str = '', prefix: str = '.',
        modules: dict = {}):
    """Save database to a JSON file.

    Args:
        api_id (Union[int, str]): The API ID.
        api_hash (str): The hash ID.
        token (str, optional): The token. Defaults to ''.
        prefix (str, optional): The prefix. Defaults to '.'.
        modules (dict, optional): The modules. Defaults to {}.
    """
    data = {
        'api_id': api_id,
        'api_hash': api_hash,
        'token': token,
        'prefix': prefix,
        'modules': modules
    }

    try:
        with open('./config.json', 'w') as file:
            json.dump(data, file, indent=4)
    except Exception:
        with open('./shika/config.json', 'w') as file:
            json.dump(data, file, indent=4)


def load_db():
    """Load database from a JSON file.

    Returns:
        dict: The loaded database data.
    """
    try:
        with open('./shika/config.json', 'r') as file:
            data = file.read()
    except Exception:
        with open('./config.json', 'r') as file:
            data = file.read()

    if not data:
        api_id = None
        api_hash = None

        def register():
            try:
                global api_id
                global api_hash

                api_id = int(input('Введите api_id: ').strip())
                if len(str(api_id)) != 8:
                    raise ValueError()

                api_hash = input('Введите api_hash: ').strip()

                save_db(str(api_id), api_hash)
            except ValueError:
                print('Неправильный api_id или api_hash')

                register()

        register()

        data = {
            'api_id': api_id,
            'api_hash': api_hash,
            'token': None,
            'prefix': '.',
            'modules': None
        }
    else:
        data = json.loads(data)

    return data
