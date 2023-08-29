import os
import sys
import time
import atexit
import logging

from pyrogram import Client, types
from subprocess import check_output
from .. import loader, utils, validators
from ..types import Config, ConfigValue
from loguru import logger

from aiogram import Bot
from aiogram.utils.exceptions import CantParseEntities, CantInitiateConversation, BotBlocked

@loader.module(name="Updater", author='shika')
class UpdateMod(loader.Module):
    """🍵 Обновление с гита shika"""
    def __init__(self):
        value = self.db.get('Updater', 'sendOnUpdate')
        
        if value is None:
            value = True
        else:
            value = self._validate_boolean(value)

        self.config = Config(
            ConfigValue(
                option='sendOnUpdate',
                default=True,
                value=value
            )  # type: ignore
        )

    def _validate_boolean(self, value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
        # Default to True if the value is invalid
        return True

    async def on_load(self, app: Client):
        if not self.config.get('sendOnUpdate'):
            return

        bot: Bot = self.bot.bot
        me = await app.get_me()
        _me = await bot.get_me()

        last = None

        try:
            last = check_output('git log -1', shell=True).decode().split()[1]
            diff = check_output('git diff', shell=True).decode()

            if diff:
                await bot.send_message(
                    me.id,
                    f"✔ Доступно обновление (<a href='https://github.com/F1reWs/Shika/commit/{last}'>{last[:6]}...</a>)"
                )
                
        except CantInitiateConversation:
            logger.error(f'Updater | Вы заблокировали ботом, пожалуйста разблокируйте бота ({_me.username})')
            await bot.send_message(
                me.id,
                '<b><emoji id=5019523782004441717>❌</emoji> Произошла ошибка, при проверке доступного обновления.</b>\n'
                f'<b><emoji id=5019523782004441717>❌</emoji> Вы заблокировали ботом, пожалуйста разблокируйте бота ({_me.username})</b>'
            )
        except BotBlocked:
            logger.error(f'Updater | Вы не начали диалог с ботом, пожалуйста напишите боту /start ({_me.username})')
            await bot.send_message(
                me.id,
                '<b><emoji id=5019523782004441717>❌</emoji> Произошла ошибка, при проверке доступного обновления.</b>\n'
                f'<b><emoji id=5019523782004441717>❌</emoji> Вы не начали диалог с ботом, пожалуйста напишите боту /start ({_me.username})</b>'
            )

        except CantParseEntities:
            await bot.send_message(
                me.id,
                f"✔ Доступно обновление (https://github.com/F1reWs/Shika/commit/{last})"
            )
        except Exception as error:
            await bot.send_message(
                me.id,
                '❌ Произошла ошибка, при проверке доступного обновления.\n'
                f'❌ Пожалуйста, удостовертесь что у вас работает команда GIT {error}'
            )

    async def update_cmd(self, app: Client, message: types.Message):
        try:
            await utils.answer(message, '<b><emoji id=5328274090262275771>🕐</emoji> Скачивание обновлений...</b>')

            check_output('git stash', shell=True).decode()
            output = check_output('git pull', shell=True).decode()
            
            if 'Already up to date.' in output:
                return await utils.answer(message, '<b><emoji id=5332533929020761310>✅</emoji> У вас уже установлена последняя версия!</b>')
            
            def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "shika")

            atexit.register(restart)
            self.db.set(
                "shika.loader", "restart", {
                    "msg": f"{message.chat.id}:{message.id}",
                    "start": str(round(time.time())),
                    "type": "update"
                }
            )

            await utils.answer(message, "<b><emoji id=5328274090262275771>🔁</emoji> Обновление...</b>")

            logging.info("Обновление...")
            return sys.exit(0)
        except Exception as error:
            await utils.answer(message, f'Произошла ошибка: {error}')
