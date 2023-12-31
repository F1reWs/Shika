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

import pyrogram
import time

from .terminal import bash_exec
from pyrogram import Client, types
from datetime import timedelta
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from .. import __version__, loader, utils, validators
from ..types import Config, ConfigValue


@loader.module(name="UserBot", author='shika')
class AboutMod(loader.Module):
    """Модуль с информацией о юзерботе"""
    def __init__(self):
        self.boot_time = time.time()
        self.config = Config(
            ConfigValue(
                option='customText',
                description='Кастомный текст сообщения в info. Может содержать ключевые слова {owner}, {cpu}, {ram}, {uptime}, {version}, {platform}, {pyro} и также HTML разметку',
                default='',
                value='',
            )
        )
    
    @loader.on_bot(lambda self, app, message: message.text and "/start" in message.text.lower())
    async def start_message_handler(self, app: Client, message: Message):
        """Start хэндлер"""
        keyboard = InlineKeyboardMarkup(
     ).add(
        InlineKeyboardButton("🐈‍⬛ Github", url="https://github.com/F1reWs/Shika"),
     ).add(
        InlineKeyboardButton("🗞 Новости", url="https://t.me/shikaub"),
        InlineKeyboardButton("💬 Чат", url="https://t.me/shika_chat"),
     )
        return await message.answer_photo(photo="https://zefirka.club/uploads/posts/2022-11/1668857696_5-zefirka-club-p-telegram-s-oboyami-dlya-telefona-5.jpg", caption="""<b>
🌀 <a href="https://github.com/F1reWs/Shika">Shika</a> - лучший и мощный Telegram юзербот!
Вы можете установить Shika на свой аккаунт.
</b>""", reply_markup=keyboard)
        
    
    async def info_cmd(self, app: Client, message: types.Message):
        """Информация о юзерботе"""
        platform = utils.get_platform()

        uptime_raw = round(time.time() - self.boot_time)
        uptime = (timedelta(seconds=uptime_raw))

        me = (await app.get_me()).first_name
        build = utils.get_commit_url()

        version = "1.0.0"

        default = f"""
<b>🌀 Shika</b>

<b><emoji id=5445284980978621387>🚀</emoji> Владелец:</b> `{me}`

<b><emoji id=5971818172985117571>💻</emoji> Версия:</b> `{version}` {build}
<b><emoji id=5451732530048802485>⏳</emoji> Аптайм:</b> `{uptime}`

<b><emoji id=5431449001532594346>⚡️</emoji> CPU:</b> `{utils.get_cpu()}%`
<b>💾 RAM:</b> `{utils.get_ram()}MB`</b>

<b>{platform}</b>
"""

        text = default
        custom = self.db.get('UserBot', 'customText')

        if custom:
            custom = custom.format(
                owner=me,
                cpu=utils.get_cpu(),
                ram=utils.get_ram(),
                uptime=uptime,
                build=utils.get_commit_url(),
                version=version,
                platform=platform,
                pyro=pyrogram.__version__
            )
        
        await utils.answer(
            message,
            custom or text,
            disable_preview=True,
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
