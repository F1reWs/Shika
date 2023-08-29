import pyrogram
import time

from .terminal import bash_exec
from pyrogram import Client, types
from datetime import timedelta
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue


@loader.module(name="UserBot", author='shika')
class AboutMod(loader.Module):
    """Модуль с информацией о юзерботе"""
    def __init__(self):
        self.boot_time = time.time()
        self.config = Config(
            ConfigValue(
                'customText',
                '',
                self.db.get('UserBot', 'customText') or ''
            )  # No need to specify validators.String() here
        )

    
    async def info_cmd(self, app: Client, message: types.Message):
        """Информация о юзерботе"""
        platform = utils.get_platform()

        uptime_raw = round(time.time() - self.boot_time)
        uptime = (timedelta(seconds=uptime_raw))

        me = (await app.get_me()).first_name

        version = "0.0.0"

        default = f"""
<b>🌀 Shika</b>

<b><emoji id=5445284980978621387>🚀</emoji> Владелец:</b> `{me}`

<b><emoji id=5971818172985117571>💻</emoji> Версия:</b> `{version}`
<b><emoji id=5451732530048802485>⏳</emoji> Аптайм:</b> `{uptime}`

<b><emoji id=5431449001532594346>⚡️</emoji> CPU:</b> `{utils.get_cpu()}%`
<b>💾 RAM:</b> `{utils.get_ram()}MB`</b>

<b>{platform}</b>
"""

        text = default
        custom = self.config.get('customText')

        if custom:
            custom = custom.format(
                owner=me,
                cpu=utils.get_cpu(),
                ram=utils.get_ram(),
                uptime=uptime,
                version=version,
                platform=platform,
                pyro=pyrogram.__version__
            )
        
        await utils.answer(
            message,
            custom or text
        )

    async def shika_cmd(self, app: Client, message: types.Message, args: str):
        """Информация о Shika"""
        await utils.answer(message, f'''<b>
🌀 Shika {__version__}

</b><i>The best userbot.</i>

<b><emoji id=5377399247589088543>🔥</emoji> Версия pyrogram: `{pyrogram.__version__}`

<emoji id=5361735750968679136>🖥</emoji> Developers: t.me/F1reW & t.me/dev_codwiz</b>
''', disable_preview=True)
        
    async def userbot_cmd(self, app: Client, message: types.Message, args: str):
        """Что такое юзербот"""
        await utils.answer(message, '''
<emoji id=5467741625507651028>🤔</emoji> <b>Что такое юзербот?</b>

<emoji id=5373098009640836781>📚</emoji> <b>Юзербот</b> представляет собой <b>сборник программ</b>, которые позволяют взаимодействовать с Telegram API. Это дает возможность создавать скрипты для автоматизации различных действий от лица пользователя, таких как <b>подписка на каналы, отправка сообщений и другие подобные задачи</b>.

<emoji id=6325536273435986182>🤔</emoji> <b>Как юзербот отличается от обычного бота?</b>

🤭 <b>Юзербот может выполняться на обычном аккаунте пользователя</b>, например, на аккаунте @paveldurov, в то время как обычные боты могут функционировать только на специальных бот-аккаунтах, например, как @examplebot. Юзерботы обладают <b>большей гибкостью в настройке и предоставляют больше функциональных возможностей</b>.

<emoji id=5467596412663372909>⁉️</emoji> <b>Поддерживаются ли юзерботы официально Telegram?</b>

<emoji id=5462882007451185227>🚫</emoji> <b>Нет, официально они не поддерживаются</b>. Тем не менее, использование юзерботов не приведет к блокировке вашего аккаунта, если вы не занимаетесь злонамеренной деятельностью или не нарушаете правила Telegram API. Важно следить за тем, чтобы ваши действия с аккаунтом оставались безопасными и законными.''')

