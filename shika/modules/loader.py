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

VALID_URL = r"[-[\]_.~:/?#@!$&'()*+,;%<=>a-zA-Z0-9]+"
VALID_PIP_PACKAGES = re.compile(
    r"^\s*# required:(?: ?)((?:{url} )*(?:{url}))\s*$".format(url=VALID_URL),
    re.MULTILINE,
)
GIT_REGEX = re.compile(
    r"^https?://github\.com((?:/[a-z0-9-]+){2})(?:/tree/([a-z0-9-]+)((?:/[a-z0-9-]+)*))?/?$",
    flags=re.IGNORECASE,
)


async def get_git_raw_link(repo_url: str):
    """Получить raw ссылку на репозиторий"""
    match = GIT_REGEX.search(repo_url)
    if not match:
        return False

    repo_path = match.group(1)
    branch = match.group(2)
    path = match.group(3)

    r = await utils.run_sync(requests.get, f"https://api.github.com/repos{repo_path}")
    if r.status_code != 200:
        return False

    branch = branch or r.json()["default_branch"]

    return f"https://raw.githubusercontent.com{repo_path}/{branch}{path or ''}/"


@loader.module(name="Loader", author='shika')
class LoaderMod(loader.Module):
    """Загрузчик модулей"""

    async def dlmod_cmd(self, app: Client, message: types.Message, args: str):
        """Загрузить модуль по ссылке. Использование: dlmod <ссылка или all или ничего>"""
        modules_repo = self.db.get(
            "shika.loader", "repo",
            "https://github.com/F1reWs/shika-mods"
        )
        api_result = await get_git_raw_link(modules_repo)
        if not api_result:
            return await utils.answer(
                message, "❌ Неверная ссылка на репозиторий.\n"
                        "Поменяй её с помощью команды: dlrepo <ссылка на репозиторий или reset>"
            )

        raw_link = api_result
        modules = await utils.run_sync(requests.get, raw_link + "all.txt")
        if modules.status_code != 200:
            return await utils.answer(
                message, (
                    f"❌ В <a href=\"{modules_repo}\">репозитории</a> не найден файл all.txt\n"
                ), disable_web_page_preview=True
            )

        modules: List[str] = modules.text.splitlines()

        if not args:
            text = (
                f"📥 Список доступных модулей с <a href=\"{modules_repo}\">репозитория</a>:\n\n"
                + "<code>all</code> - загрузит все модули\n"
                + "\n".join(
                    map("<code>{}</code>".format, modules))
            )
            return await utils.answer(
                message, text, disable_web_page_preview=True)

        error_text: str = None
        module_name: str = None
        count = 0

        if args == "all":
            for module in modules:
                module = raw_link + module + ".py"
                try:
                    r = await utils.run_sync(requests.get, module)
                    if r.status_code != 200:
                        raise requests.exceptions.RequestException
                except requests.exceptions.RequestException:
                    continue

                if not (module_name := await self.all_modules.load_module(r.text, r.url)):
                    continue

                self.db.set("shika.loader", "modules",
                            list(set(self.db.get("shika.loader", "modules", []) + [module])))
                count += 1
        else:
            if args in modules:
                args = raw_link + args + ".py"

            try:
                r = await utils.run_sync(requests.get, args)
                if r.status_code != 200:
                    raise requests.exceptions.ConnectionError

                module_name = await self.all_modules.load_module(r.text, r.url)
                if module_name is True:
                    error_text = "✅ Зависимости установлены. Требуется перезагрузка"

                if not module_name:
                    error_text = "❌ Не удалось загрузить модуль. Подробности смотри в логах"
            except requests.exceptions.MissingSchema:
                error_text = "❌ Ссылка указана неверно"
            except requests.exceptions.ConnectionError:
                error_text = "❌ Модуль недоступен по ссылке"
            except requests.exceptions.RequestException:
                error_text = "❌ Произошла непредвиденная ошибка. Подробности смотри в логах"

            if error_text:
                return await utils.answer(message, error_text)

            self.db.set("shika.loader", "modules",
                        list(set(self.db.get("shika.loader", "modules", []) + [args])))

        return await utils.answer(
            message, (
                f"✅ Модуль \"<code>{module_name}</code>\" загружен"
                if args != "all"
                else f"✅ Загружено <b>{count}</b> из <b>{len(modules)}</b> модулей"
            )
        )

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
                message, "❌ Нет реплая на файл")

        file = await reply.download()

        modules = [
            'config',
            'eval',
            'help',
            'info',
            'moduleGuard',
            'terminal',
            'tester',
            'updater'
        ]
        
        for mod in modules:
            if file == mod:
                return await utils.answer(
                    message,
                    "❌ Нельзя загружать встроенные модули"
                )

        try:
            with open(file, "r", encoding="utf-8") as file:
                module_source = file.read()
        except UnicodeDecodeError:
            return await utils.answer(
                message, "❌ Неверная кодировка файла")

        module_name = await self.all_modules.load_module(module_source)

        if module_name is True:
            return await utils.answer(
                message, "✅ Зависимости установлены. Требуется перезагрузка")

        if not module_name:
            return await utils.answer(
                message, "❌ Не удалось загрузить модуль. Подробности смотри в логах")
        
        module = '_'.join(module_name.lower().split())
        with open(f'shika/modules/{module}.py', 'w', encoding="utf-8") as file:
            file.write(module_source)
        
        return await utils.answer(
            message, f"✅ Модуль \"<code>{module_name}</code>\" загружен")
    
    async def ml_cmd(self, app: Client, message: types.Message, args: str):
        """Скинуть файл модуля"""
        app.me = await app.get_me()
        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]
        if not args:
            return await utils.answer(
            message, "<emoji id=5312526098750252863>❌</emoji> <b>Вы не указали модуль</b>")

        await message.edit(f"<emoji id=5327902038720257153>🔄</emoji><b>Отправляю модуль...</b>")
        module = args.split(maxsplit=1)[0].replace('.py', '')
        if module + '.py' not in os.listdir('./shika/modules'):
            mods = self.db.get("shika.loader", "modules")
            for mod in mods:
                if module in mod:
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
                message, "❌ Неверное название модуля")
        
        modules = [
            'config',
            'eval',
            'help',
            'info',
            'moduleGuard',
            'terminal',
            'tester',
            'updater'
        ]
        
        if module_name in modules:
            return await utils.answer(
                message,
                "❌ Выгружать встроенные модули нельзя"
            )

        return await utils.answer(
            message, f"✅ Модуль \"<code>{module_name}</code>\" выгружен")
    
    async def reloadmod_cmd(self, app: Client, message: types.Message, args: str):
        if not args:
            return await utils.answer(
                message, "❌ Вы не указали модуль")
        
        try:
            module = args.split(maxsplit=1)[0].replace('.py', '')

            modules = [
                'config',
                'eval',
                'help',
                'info',
                'moduleGuard',
                'terminal',
                'tester',
                'updater',
                'loader'
            ]
            
            for mod in modules:
                if module == mod:
                    return await utils.answer(
                        message,
                        "❌ Нельзя перезагружать встроенные модули"
                    )

            if module + '.py' not in os.listdir('shika/modules'):
                return await utils.answer(
                    message,
                    f'❌ Модуль {module} не найден'
                )
            
            unload = self.all_modules.unload_module(module)
            with open('shika/modules/' + module + '.py', 'r', encoding='utf-8') as file:
                module_source = file.read()

            load = await self.all_modules.load_module(module_source)

            if not load and not unload:
                return await utils.answer(
                    message,
                    '❌ Произошла ошибка, пожалуйста проверьте логи'
                )
        except Exception as error:
            logging.error(error)
            return await utils.answer(
                message,
                '❌ Произошла ошибка, пожалуйста проверьте логи'
            )


        return await utils.answer(
            message, f"✅ Модуль \"<code>{module}</code>\" перезагружен")

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
                message, "❌ Нет аргументов")

        if args == "reset":
            self.db.set(
                "shika.loader", "repo",
                "https://github.com/CodWize/shika-modules"
            )
            return await utils.answer(
                message, "✅ Ссылка на репозиторий была сброшена")

        if not await get_git_raw_link(args):
            return await utils.answer(
                message, "❌ Ссылка указана неверно")

        self.db.set("shika.loader", "repo", args)
        return await utils.answer(
            message, "✅ Ссылка на репозиторий установлена")
