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

from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, InlineQuery,
    InlineQueryResultArticle, InputTextMessageContent,
    Message
)
from inspect import getmembers, isroutine
from pyrogram import Client, types
from asyncio import sleep

from .. import loader, utils, database, validators
from ..types import ConfigValue

# distutils will be deleted in python 3.12
# distutils будет удалена в python 3.12
def strtobool(val):
    # distutils.util.strtobool
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))

@loader.module(name="config", author="shika", version=1)
class ConfigMod(loader.Module):
    """Настройка модулей"""

    def __init__(self):
        self.inline_bot = self.bot.bot
        self._dp = self.bot._dp
        self.DEFAULT_ATTRS = [
            'all_modules', 'author', 'bot', 'callback_handlers',
            'command_handlers', 'inline_handlers', 'bot_username',
            'message_handlers', 'name', 'version', 'watcher_handlers',
            'boot_time', 'shika.bot', 'shika.loader', 'shika.me', 'Updater',
        ]
        self.config = None  # Пoявляется после get_attrs
        self.pending = False
        self.pending_id = utils.random_id(50)
        self.pending_module = False
        self.pending_edit = False

    def get_module(self, data: str) -> loader.Module:
        return next((module for module in self.all_modules.modules if module.name.lower() in data.lower()), None)
    
    def validate(self, attribute):
        if isinstance(attribute, str):
            try:
                attribute = int(attribute)
            except:
                try:
                    attribute = bool(strtobool(attribute))
                except:
                    pass

        return attribute

    def get_attrs(self, module):
        attrs = getmembers(module, lambda a: not isroutine(a))
        attrs = [
            (key, value) for key, value in attrs if not (
                key.startswith('__') and key.endswith('__')
            ) and key not in self.DEFAULT_ATTRS
        ]
        if len(attrs) > 1:
            self.config = getattr(module, attrs[0][0])
            self.config_db: database.Database = attrs[1][1]

            return attrs[0][1]
        
        return []

    @loader.on_bot(lambda _, __, call: call.data == "send_cfg")
    async def config_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.db.get("shika.me", "id"):
            return await call.answer('Ты не владелец')

        inline_keyboard = InlineKeyboardMarkup(row_width=3, resize_keyboard=True)
        modules = [mod for mod in self.all_modules.modules]
        message: Message = await self.inline_bot.edit_message_text(inline_message_id=call.inline_message_id, text="<b>🌀 Shika</b>", reply_markup=inline_keyboard)

        if self.pending:
            self.pending, self.pending_module, self.pending_id = False, utils.random_id(50), False

        count = 1
        buttons = []

        for module in modules:
            name = module.name

            attrs = self.get_attrs(module)

            if not attrs:
              pass

            con = 1

            for namee in attrs:
               if namee not in self.DEFAULT_ATTRS:
                 con += 1
        
            if con == 1:
               pass

            if 'config' in name.lower():
                continue

            if attrs and con != 1:
               data = f'mod_{name}|{call.inline_message_id}'
               buttons.append(InlineKeyboardButton(name, callback_data=str(data)))

               if count % 3 == 0:
                   inline_keyboard.row(*buttons)
                   buttons.clear()

            count += 1

        if buttons:
            inline_keyboard.row(*buttons)

        await self.inline_bot.edit_message_text(
inline_message_id=call.inline_message_id,
text="<b>🌀 Shika</b>",
reply_markup=inline_keyboard)

    @loader.on_bot(lambda _, __, call: call.data.startswith('mod'))
    async def answer_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.db.get("shika.me", "id"):
            return await call.answer('Ты не владелец')
        data = call.data
        data_parts = data.split('|')
        message = data_parts[1]
        self.message = message

        keyboard = InlineKeyboardMarkup()
        mod = self.get_module(data)
        attrs = self.get_attrs(mod)

        if not attrs:
            return await call.answer('😞 У этого модуля нету атрибутов', show_alert=False)

        buttons = []
        count = 1
        con = 1

        for name in attrs:
          if name not in self.DEFAULT_ATTRS:
            con += 1
        
        if con == 1:
            return await call.answer('😞 У этого модуля нету атрибутов', show_alert=False)

        for name in attrs:
          if name not in self.DEFAULT_ATTRS:
            buttons.append(
                InlineKeyboardButton(
                    name, callback_data=f'ch_attr_{mod.name.split(".")[-1]}_{name}'
                )
            )

            if count % 3 == 0:
                keyboard.row(*buttons)
                buttons.clear()

            count += 1

        if buttons:
            keyboard.row(*buttons)

        keyboard.add(InlineKeyboardButton('↪️ Назад', callback_data='send_cfg'))
        
        attributes = []
        for key, value in attrs.items():
            formated = str(value)
            if isinstance(value, tuple):
                formated = ', '.join(f"{k}: {v}" for k, v in value)

            attributes.append(f'<b>➡ <b>(Тип {type(value).__name__})</b> <code>{key}</code>: <code>{formated}</code></b>')

        attributes_text = '\n'.join(attributes)

        await self.inline_bot.edit_message_text(
inline_message_id=call.inline_message_id,
text=f'<b>⚙️ Модуль: <code>{mod.name}</code>\n\n{attributes_text}</b>',
reply_markup=keyboard)

    @loader.on_bot(lambda _, __, call: call.data.startswith('ch_attr_'))
    async def change_attribute_callback_handler(self, app: Client, call: CallbackQuery):
      if call.from_user.id == self.db.get("shika.me", "id"):
        self.bot_username = (await self.bot.bot.get_me()).username
        data = call.data.replace('ch_attr_', '').split('_')
        module = data[0]
        attribute = data[1]

        module = self.get_module(module)

        self.pending = attribute
        self.pending_module = module
        self.pending_id = utils.random_id(7)

        standart_arg = self.config.get_default(self.pending)
        descr = self.config.get_description(self.pending)

        now_data = self.db.get(self.pending_module.name, attribute)

        description = f"ℹ️ {descr}"
        self.pending_module_description = description

        data_type = type(standart_arg).__name__

        if data_type == "str":
            what_data = "текстом"
        elif data_type == "bool":
            what_data = "True либо False"
        elif data_type == "int":
            what_data = "цифрой"
        elif data_type == "float":
            what_data = "цифрой"
        elif data_type == "list":
            what_data = "списком"
        elif data_type == "NoneType":
            what_data = "текстом или другим, завысить от того для чего это значение"
        else:
            what_data = data_type

        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton(
                '✍️ Ввести значение',
                callback_data='aaa'
            ),
        )
        keyboard.row(
            InlineKeyboardButton(
                '♻️ Значение по умолчанию',
                callback_data='bbb'
            ),
        )
        keyboard.row(
            InlineKeyboardButton(
                '↪️ Вернутся',
                callback_data='send_cfg'
            ),
        )
        
        await self.inline_bot.edit_message_text(
inline_message_id=call.inline_message_id,
text=f'''<b>⚙️ Модуль: <code>{self.pending_module.name}</code>
➡ Атрибут: <code>{attribute}</code>

</b><i>{description}</i><b>

Стандарт: <code>{standart_arg}</code>

Текущее: <code>{now_data}</code>

📁 Должно быть {what_data}
</b>''',
reply_markup=keyboard)

    @loader.on_bot(lambda _, __, data: data.data == 'aaa')
    async def aaa_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != self.db.get("shika.me", "id"):
            return await call.answer('Ты не владелец')
        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton(
                '↪️ Вернутся',
                callback_data='send_cfg'
            ),
        )

        self.pending_edit = "new"

        await self.inline_bot.edit_message_text(
inline_message_id=call.inline_message_id,
text=f'''<b>
☝️ Что бы сменить значение, напишите вашему боту (@{self.bot_username}) сообщение <code>{self.pending_id} тут_новое_значение</code>
</b>''', 
reply_markup=keyboard)
        
    @loader.on_bot(lambda _, __, data: data.data == 'bbb')
    async def bbb_callback_handler(self, app: Client, call: CallbackQuery):
        if call.from_user.id != (await app.get_me()).id:
            return await call.answer('Ты не владелец')
        keyboard = InlineKeyboardMarkup()

        keyboard.row(
            InlineKeyboardButton(
                '↪️ Вернутся',
                callback_data='send_cfg'
            ),
        )

        self.pending_edit = "standart"

        await self.inline_bot.edit_message_text(
inline_message_id=call.inline_message_id,
text=f'''<b>
☝️ Что бы поставить значение по умолчанию, напишите вашему боту (@{self.bot_username}) сообщение <code>{self.pending_id}</code>
</b>''', 
reply_markup=keyboard)

    @loader.on_bot(lambda self, __, msg: len(self.pending_id) != 50)
    async def change_message_handler(self, app: Client, message: Message):
      if self.pending_id in message.text:
        if message.from_user.id != self.db.get("shika.me", "id"):
            return
        if self.pending_id in message.text:
          if self.pending_edit == "new":
            attr = message.text.replace(self.pending_id, '').strip()

            attribute: ConfigValue = self.config[self.pending]
            self.config[self.pending] = self.validate(attr)
            self.config_db.set(
                self.pending_module.name,
                self.pending,
                self.validate(attr)
            )

            message = await message.reply('<b>📝 Значение успешно изменено!</b>')

          if self.pending_edit == "standart":
            standart_arg = self.config.get_default(self.pending)

            self.config_db.set(
                self.pending_module.name,
                self.pending,
                standart_arg
            )

            message = await message.reply('<b>📝 Значение успешно изменено на стандартное!</b>')

          self.pending, self.pending_id, self.pending_module = False, utils.random_id(50), False

          self.pending_edit = False

    async def cfg_inline_handler(self, app: Client, inline_query: InlineQuery):
        if inline_query.from_user.id == self.db.get("shika.me", "id"):
            await self.set_cfg(inline_query)

    async def set_cfg(self, inline_query):
        await inline_query.answer(
            [
                InlineQueryResultArticle(
                    id=utils.random_id(),
                    title="Конфиг модулей",
                    input_message_content=InputTextMessageContent("<b>🌀 Shika</b>"),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("🗂 Открыть config", callback_data="send_cfg")
                    )
                )
            ]
        )

    async def config_cmd(self, app: Client, message: types.Message):
        """Настройка через inline"""
        bot = await self.inline_bot.get_me()
        await utils.answer_inline(message, bot.username, 'cfg')
        await message.delete()

