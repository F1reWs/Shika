from pyrogram import Client, types
from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent, CallbackQuery
)
from .. import loader, utils

@loader.module(name="pg")
class ExampleMod(loader.Module):
    """Packages Manager"""

    async def pg_cmd(self, app: Client, message: types.Message):
        """main."""
        bot = (await self.bot.bot.get_me()).username

        await utils.answer_inline(
            message,
            bot,
            'pg'
        )
    
    async def pg_inline_handler(self, app, query: InlineQuery):
        await query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(10),
                    title='Packages',
                    input_message_content=InputTextMessageContent('idk...'),
                    reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('❌ Закрыть', callback_data='close'))
                )
            ]
        )
    
    @loader.on_bot(lambda _, __, call: call.data == 'close')
    async def close_callback_handler(self, app, call: CallbackQuery):
        # все ебашь сюда ваватинг
        ...
