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
from aiogram.types import InputFile
from aiogram.utils.exceptions import CantParseEntities, CantInitiateConversation, BotBlocked
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    Message
)

@loader.module(name="Updater", author='Shika')
class UpdateMod(loader.Module):
    """Обновление Shika"""
    def __init__(self):
        value = self.db.get('Updater', 'sendOnUpdate')
        self.inline_bot = self.bot.bot
        
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
        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]

        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton(
                '🔄 Обновить',
                callback_data='update_from_bot'
            ),
            InlineKeyboardButton(
                '🚫 Не обновляться',
                callback_data='not_update_from_bot'
            ),
        )

        last = None

        try:
            last = check_output('git log -1', shell=True).decode().split()[1]
            diff = check_output('git diff', shell=True).decode()

            if diff:
             gif_path = './assets/update.mp4'

             with open(gif_path, 'rb') as gif_file:
               await bot.send_video(chat_id=me.id, caption=f"""<b>
🔍 Доступно обновление Shika (<a href='https://github.com/F1reWs/Shika/commit/{last}'>{last[:6]}...</a>)
</b>""", reply_markup=keyboard, video=InputFile(gif_file))

        except CantInitiateConversation:
            logger.error(f'Updater | Вы заблокировали ботом, пожалуйста разблокируйте бота ({_me.username})')
        except BotBlocked:
            logger.error(f'Updater | Вы не начали диалог с ботом, пожалуйста напишите боту /start ({_me.username})')

        except CantParseEntities:
            gif_path = './assets/update.mp4'

            with open(gif_path, 'rb') as gif_file:
               await bot.send_video(chat_id=me.id, caption=f"""<b>
🔍 Доступно обновление Shika (<a href='https://github.com/F1reWs/Shika/commit/{last}'>{last[:6]}...</a>)
</b>""", reply_markup=keyboard, video=InputFile(gif_file))
        except Exception as error:
            await bot.send_message(
                me.id,
                '<b>❌ Произошла ошибка, при проверке доступного обновления.</b>\n',
                f'<b>❌ Пожалуйста, удостовертесь что у вас работает команда GIT {error}</b>'
            )
        except:
            await bot.send_message(
                me.id,
                '<b>❌ Произошла ошибка, при проверке доступного обновления.</b>\n',
            )

    @loader.on_bot(lambda _, __, call: call.data.startswith('update_from_bot'))
    async def answer_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != (await app.get_me()).id:
            return await call.answer('Ты не владелец')
        
        await call.message.delete()

        msg = await call.message.answer(text=f'<b>🕐 Скачивание обновлений...</b>',)
        
        check_output('git stash', shell=True).decode()
        output = check_output('git pull', shell=True).decode()
            
        if 'Already up to date.' in output:
            return await msg.edit_text(
text=f'<b>✅ У вас уже установлена последняя версия!</b>',)
        
        def restart() -> None:
                os.execl(sys.executable, sys.executable, "-m", "shika")

        atexit.register(restart)
        self.db.set(
                "shika.loader", "restart", {
                    "msg": f"{msg.chat.id}:{msg.message_id}",
                    "start": str(round(time.time())),
                    "type": "update"
                }
            )

        await msg.edit_text(
text=f'<b>🔄 Обновление...</b>',)

        logging.info("Обновление...")
        return sys.exit(0)

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
