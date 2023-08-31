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

from subprocess import check_output
from pyrogram import Client, types

from .. import loader, utils
from ..wrappers import wrap_function_to_async

@wrap_function_to_async
def bash_exec(args: str):
    try:
        output = check_output(args.strip(), shell=True)
        output = output.decode()

        return output
    except UnicodeDecodeError:
        return check_output(args.strip(), shell=True)
    except Exception as error:
        return error


@loader.module(name="Terminal", author='F1reW')
class TerminalMod(loader.Module):
    """Терминал"""
    async def terminal_cmd(self, app: Client, message: types.Message, args: str):
        output = await bash_exec(args)

        await utils.answer(
            message,
            f"""
<emoji id=5472111548572900003>⌨️</emoji> <b>Команда:</b> <code>{args.strip()}</code>
💾 <b>Вывод:</b><code>
{output}
</code>
        """
        )
