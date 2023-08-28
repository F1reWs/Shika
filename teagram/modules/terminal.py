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
