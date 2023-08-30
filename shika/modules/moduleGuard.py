from pyrogram import Client, types
from .. import loader, utils, validators
from ..types import Config, ConfigValue

import os

@loader.module(name="ModuleGuard", author='shika')
class ModuleGuardMod(loader.Module):
    """moduleGuard оповестит вас о вредоносном модуле."""
    def __init__(self):
        self.config = Config(
            ConfigValue(
                option='send',
                description='Будет ли проверка модулей на вредоносный модуль',
                default=True,
                value=True,
            )
        )


    async def on_load(self, app: types.Message):
        if self.db.get('ModuleGuard', 'send') == True:
            names = {
                "info": [
                    {"id": "other", "name": "other"},
                    {"id": "other", "name": "other"}
                ],
                "warns": [
                    {"id": "eval", "name": "Eval"},
                    {"id": "exec", "name": "Exec"}
                ],
                "criticals": [
                    {"id": "session", "name": "plugin can get session"},
                    {"id": "db.json", "name": "plugin can get auth data (db.json)"},
                    {"id": "config.ini", "name": "plugin can get auth data (config.ini)"}
                ]
            }

            basic_plugins = ['eval.py', '_example.py', 'help.py', 
                            'info.py', 'loader.py', 'moduleGuard.py',
                            'terminal.py', 'tester.py', 'translator.py',
                            'updater.py', 'backup.py', 'config.py']
                            
            critical = []
            warns = []
            info = []
            file_list = os.listdir("shika/modules/")

            for file_name in file_list:
                if file_name in basic_plugins:
                    continue
                else:
                    file_path = os.path.join("shika/modules/", file_name)
                    if os.path.isfile(file_path):
                        with open(file_path, "r") as file:
                            try:
                                content = file.read()
                            except UnicodeDecodeError:
                                continue

                        for word in names["warns"]:
                            if word['id'] in content:
                                warns.append(word["name"])

                        for word in names["criticals"]:
                            if word['id'] in content:
                                critical.append(word["name"])

                        # for word in names["info"]:
                        #     if word['id'] in content:
                        #         info.append(word["name"])

            message_text = """
<b><emoji id=5197373721987260587>🔒</emoji> ModuleGuard</b>
    """
            basic_text = """
<b><emoji id=5197373721987260587>🔒</emoji> ModuleGuard</b>
    """
            for file_name in file_list:
                if not file_name.endswith('.py'):
                    continue
                if file_name in basic_plugins:
                    continue
                else:
                    info_text = ', '.join(info)
                    warns_text = ', '.join(warns)
                    critical_text = ', '.join(critical)
                    message_text += f"{file_name}:\n"

                    if info_text:
                        message_text += f"<b>❔ Info ➜ {info_text}</b>\n"
                    if warns_text:
                        message_text += f"<b>❗ Warns ➜ {warns_text}</b>\n"
                    if critical_text:
                        message_text += f"<b>❌ Criticals ➜ {critical_text}</b>\n"

                    if not info and not warns and not critical:
                        message_text += 'Безопасный плагин ✔\n'
            
            if message_text == basic_text:
                message_text += '<b><emoji id=5332533929020761310>✅</emoji> Подозрительных плагинов не найдено</b>'

            await app.send_message("me", message_text)