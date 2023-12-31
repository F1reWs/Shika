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

import logging
import asyncio

import io
import os
import re
import sys
import time

import atexit
import tempfile

import requests

from typing import List

from git import Repo
from git.exc import GitCommandError

from pyrogram import Client, types
from .. import loader, utils
from ..types import Config, ConfigValue

VALID_URL = r"[-[\]_.~:/?#@!$&'()*+,;%<=>a-zA-Z0-9]+"
VALID_PIP_PACKAGES = re.compile(
    r"^\s*# required:(?: ?)((?:{url} )*(?:{url}))\s*$".format(url=VALID_URL),
    re.MULTILINE,
)

GIT_REPO_REGEX = re.compile(r'^https://github\.com/([^/]+)/([^/]+)$')

async def get_git_raw_link(repo_url: str) -> str:
    match = GIT_REPO_REGEX.search(repo_url)
    if not match:
        raise ValueError("Недопустимая ссылка на репозиторий GitHub")

    owner = match.group(1)
    repo = match.group(2)

    response = await utils.run_sync(requests.get, f"https://api.github.com/repos/{owner}/{repo}")
    if response.status_code == 200:
         default_branch = response.json().get("default_branch", "main")
    else:
         default_branch = "main" 

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/"

    return raw_url


@loader.module(name="Loader", author='shika')
class LoaderMod(loader.Module):
    """Загрузчик модулей"""

    def __init__(self):
        self.boot_time = time.time()
        self.config = Config(
            ConfigValue(
                option='repo',
                description='Ссылка на репозиторий модулей',
                default='https://github.com/F1reWs/shika_modules',
                value='https://github.com/F1reWs/shika_modules',
            )
        )

    async def dlmod_cmd(self, app: Client, message: types.Message, args: str):
        """Загрузить модуль по ссылке. Использование: dlmod <ссылка или название модуля>"""
        modules_repo = self.db.get("Loader", "repo")
        mod = None
        error_text = False
        
        if not modules_repo:
            modules_repo = "https://github.com/F1reWs/shika_modules"
            self.db.set("Loader", "repo", modules_repo)

        if not args:
            return await utils.answer(message, "<emoji id=5312526098750252863>❌</emoji> <b>Вы не указали ссылку/название модуля</b>")

        await message.edit(f"<b><emoji id=5325792861885570739>🔄</emoji> Устанавливаю модуль...</b>")

        if modules_repo:
            api_result = await get_git_raw_link(modules_repo)
            if api_result:
                raw_link = api_result
                old_args = args
                args = raw_link + args + ".py"
        try:
            r = await utils.run_sync(requests.get, args)
            r.raise_for_status()  # Бросить исключение, если запрос завершился неудачей

            mod = await self.all_modules.load_module(r.text, r.url)
            if mod is True:
                error_text = f"<emoji id=5348498983884960309>🚀</emoji> <b>Зависимости установлены, но нужна перезагрузка </b>{prefix}restart"

            if not mod:
                error_text = "<b><emoji id=5312526098750252863>❌</emoji> Не удалось загрузить модуль. Подробности смотри в логах</b>"
        except requests.exceptions.MissingSchema:
            error_text = "<emoji id=5312526098750252863>❌</emoji><b> Ссылка указана неверно</b>"
        except requests.exceptions.RequestException as e:
            args = old_args
            try:
              r = await utils.run_sync(requests.get, args)
              r.raise_for_status()  # Бросить исключение, если запрос завершился неудачей

              mod = await self.all_modules.load_module(r.text, r.url)
              if mod is True:
                  error_text = f"<emoji id=5348498983884960309>🚀</emoji> <b>Зависимости установлены, но нужна перезагрузка </b>{prefix}restart"

              if not mod:
                   error_text = "<emoji id=5312526098750252863>❌</emoji><b> Не удалось загрузить модуль. Подробности смотри в логах</b>"
            except requests.exceptions.MissingSchema:
                 error_text = "<emoji id=5312526098750252863>❌</emoji><b> Ссылка указана неверно</b>"
            except requests.exceptions.RequestException as e:
               error_text = f"<emoji id=5312526098750252863>❌</emoji><b> Произошла ошибка при запросе:</b> {str(e)}"

        if error_text:
            return await utils.answer(message, error_text)

        self.db.set("shika.loader", "modules", list(set(self.db.get("shika.loader", "modules", []) + [args])))
        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]

        command_descriptions = ""
        inline_descriptions = ""
        module_version = ""
        module_author = ""

        command_descriptions = "\n".join(
            f"<emoji id=5100862156123931478>🔸</emoji> <code>{prefix + command}</code> {mod.command_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in mod.command_handlers
        )
        inline_descriptions = "\n".join(
            f"<emoji id=5100862156123931478>🔸</emoji> <code>@{self.bot_username + ' ' + command}</code> {mod.inline_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in mod.inline_handlers
        )

        if mod.version:
            module_version = f" (<code>{mod.version}</code>)"

        if mod.author:
            module_author = f"<b><emoji id=5220156998779152370>❤️</emoji> by <code>{mod.author}</code></b>"
        
        return await utils.answer(
            message, f"""<b>
<emoji id=5891237108974095799>🌈</emoji> Модуль <code>{mod.name}</code>{module_version} загружен {utils.ascii_face}
<emoji id=5983568653751160844>ℹ️</emoji> </b><i>{mod.__doc__ or 'Нет описания для модуля'}</i>

{command_descriptions}
{inline_descriptions}
{module_author}
""")

    async def loadmod_cmd(self, app: Client, message: types.Message):
        """Загрузить модуль по файлу. Использование: <реплай на файл>"""
        reply = message.reply_to_message
        file = (
            message
            if message.document
            else reply
            if reply and reply.document
            else None
        )

        if not file:
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji><b> Нет реплая на файл</b>")
        
        await message.edit(f"<b><emoji id=5325792861885570739>🔄</emoji> Устанавливаю модуль...</b>")

        file = await reply.download()

        modules = [
            'config',
            'eval',
            'help',
            'userbot',
            'moduleGuard',
            'terminal',
            'tester',
            'updater',
            'backuper',
        ]
        
        for mod in modules:
            if file == mod:
                return await utils.answer(
                    message,
                    "<emoji id=5312526098750252863>❌</emoji><b> Нельзя загружать встроенные модули</b>"
                )

        try:
            with open(file, "r", encoding="utf-8") as file:
                module_source = file.read()
        except UnicodeDecodeError:
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji><b> Неверная кодировка файла</b>")

        mod = await self.all_modules.load_module(module_source)
        module_name = mod.name

        if module_name is True:
            return await utils.answer(
                message, "✅ Зависимости установлены. Требуется перезагрузка")

        if not module_name:
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji><b> Не удалось загрузить модуль. Подробности смотри в логах</b>")
        
        module = '_'.join(module_name.lower().split())
        with open(f'shika/modules/{module}.py', 'w', encoding="utf-8") as file:
            file.write(module_source)

        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]

        command_descriptions = ""
        inline_descriptions = ""
        module_version = ""
        module_author = ""

        command_descriptions = "\n".join(
            f"<emoji id=5100862156123931478>🔸</emoji> <code>{prefix + command}</code> {mod.command_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in mod.command_handlers
        )
        inline_descriptions = "\n".join(
            f"<emoji id=5100862156123931478>🔸</emoji> <code>@{self.bot_username + ' ' + command}</code> {mod.inline_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in mod.inline_handlers
        )

        if mod.version:
            module_version = f" (<code>{mod.version}</code>)"

        if mod.author:
            module_author = f"<b><emoji id=5220156998779152370>❤️</emoji> by <code>{mod.author}</code></b>"
        
        return await utils.answer(
            message, f"""<b>
<emoji id=5891237108974095799>🌈</emoji> Модуль <code>{module_name}</code>{module_version} загружен {utils.ascii_face}
<emoji id=5983568653751160844>ℹ️</emoji> </b><i>{mod.__doc__ or 'Нет описания для модуля'}</i>

{command_descriptions}
{inline_descriptions}
{module_author}
""")
    
    async def ml_cmd(self, app: Client, message: types.Message, args: str):
        """Скинуть файл модуля"""
        app.me = await app.get_me()
        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]
        if not args:
            return await utils.answer(
            message, "<emoji id=5312526098750252863>❌</emoji> <b>Вы не указали модуль</b>")

        await message.edit(f"<emoji id=5327902038720257153>🔄</emoji><b>Отправляю модуль...</b>")
        module = args
        module_l = module.lower()
        if module + '.py' not in os.listdir('./shika/modules'):
            mods = self.db.get("shika.loader", "modules")
            if mods:
             for mod in mods:
                if module_l in mod.lower():
                    response = requests.get(mod)
                    content = response.content
                    file = io.BytesIO(content)
                    await message.reply_document(file_name=module+".py", document=file, caption=f'''<b>
<emoji id=5433653135799228968>📁</emoji> Модуль <code>{module}</code>

<emoji id=5318808961594437445>🌐</emoji> <a href="{mod}">Ссылка</a> на <code>{module}</code>

<emoji id=6334353510582191829>⬇️</emoji> <code>{prefix}dlmod {mod}</code>
</b>''',
                )
                    return await message.delete()
            return await utils.answer(
                    message,
                    f'<emoji id=5312526098750252863>❌</emoji> <b>Модуль <code>{module}</code> не найден</b>'
                )
        with open('./shika/modules/' + module + '.py', 'rb') as file:
            await message.reply_document(document=file, caption=f"""<b>
<emoji id=5433653135799228968>📁</emoji> Модуль <code>{module}</code>

<emoji id=6334353510582191829>⬇️</emoji> Напишите <code>{prefix}loadmod</code> в ответ на это сообщение, что бы установить
</b>""", file_name=module+".py")
            await message.delete()

    async def unloadmod_cmd(self, app: Client, message: types.Message, args: str):
        """Выгрузить модуль. Использование: unloadmod <название модуля>"""
        if not (module_name := self.all_modules.unload_module(args)):
            return await utils.answer(
                message, "<b><emoji id=5312526098750252863>❌</emoji> Неверное название модуля</b>")
        
        modules = [
            'config',
            'eval',
            'help',
            'userbot',
            'moduleGuard',
            'terminal',
            'tester',
            'updater',
            'backuper'
        ]

        for mods in modules:
          if module_name.lower() in mods.lower():
            return await utils.answer(
                message,
                "<emoji id=5312526098750252863>❌</emoji><b> Выгружать встроенные модули нельзя</b>"
            )
        
        module = '_'.join(module_name.lower().split())
        try:
            os.remove(f'shika/modules/{module}.py')
        except:
            pass

        return await utils.answer(
            message, f"<emoji id=6334758581832779720>✅</emoji><b> Модуль \"<code>{module_name}</code>\" выгружен</b>")

    async def restart_cmd(self, app: Client, message: types.Message, update: bool = False):
        """Перезагрузка юзербота"""
        def restart() -> None:
            """Запускает загрузку юзербота"""
            os.execl(sys.executable, sys.executable, "-m", "shika")

        atexit.register(restart)
        self.db.set(
            "shika.loader", "restart", {
                "msg": f"{message.chat.id}:{message.id}",
                "start": time.time(),
                "type": "restart"
            }
        )

        await utils.answer(message, "<b><emoji id=5328274090262275771>🔁</emoji> Перезагрузка...</b>")

        logging.info("Перезагрузка...")
        return sys.exit(0)


    async def dlrepo_cmd(self, app: Client, message: types.Message, args: str):
        """Установить репозиторий с модулями. Использование: dlrepo <ссылка на репозиторий или reset>"""
        if not args:
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji> <b>Нет аргументов</b>")

        if args == "reset":
            self.db.set(
                "shika.loader", "repo",
                "https://github.com/F1reWs/shika_modules"
            )
            return await utils.answer(
                message, "<emoji id=6334758581832779720>✅</emoji><b> Ссылка на репозиторий была сброшена</b>")

        if not await get_git_raw_link(args):
            return await utils.answer(
                message, "<emoji id=5312526098750252863>❌</emoji><b> Ссылка указана неверно</b>")

        self.db.set("shika.loader", "repo", args)
        return await utils.answer(
            message, "<emoji id=6334758581832779720>✅</emoji><b> Ссылка на репозиторий установлена</b>")
