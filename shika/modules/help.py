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

from pyrogram import Client, types

from .. import __version__, loader, utils


@loader.module(name="Help", author='shika', tag='system')
class HelpMod(loader.Module):
    """Помощь по командам"""
    async def help_cmd(self, app: Client, message: types.Message, args: str):
        """Список всех модулей"""
        self.bot_username = (await self.bot.bot.get_me()).username

        if not args:
            text = ""
            for module in sorted(self.all_modules.modules, key=lambda mod: len(str(mod))):
                if module.name.lower() == 'help':
                    continue

                commands = inline = ""
                prefix = self.db.get("shika.loader", "prefixes", ["."])[0]

                commands += " <b>|</b> ".join(
                    f"<code>{prefix}{command}</code>" for command in module.command_handlers
                )

                if module.inline_handlers:
                    if commands:
                        inline += " <b>| [inline]</b>: "
                    else:
                        inline += "<b>[inline]</b>: "

                inline += " <b>|</b> ".join(
                    f"<code>{inline_command}</code>" for inline_command in module.inline_handlers
                )

                if not commands and not inline:
                    pass
                else:
                    text += f"\n<emoji id=4971987363145188045>🔹</emoji> <b>{module.name}</b> - "  + (commands if commands else '`Команд не найдено`') + inline

            return await utils.answer(
                message, 
                f"<b><emoji id=5226512880362332956>📖</emoji> {len(self.all_modules.modules)-1} модулей доступно</b>\n"
                f"{text}"
            )

        if not (module := self.all_modules.get_module(args)):
            return await utils.answer(
                message, "<b><emoji id=5465665476971471368>❌</emoji> Такого модуля нет</b>")

        prefix = self.db.get("shika.loader", "prefixes", ["."])[0]

        command_descriptions = "\n".join(
            f"<emoji id=5100862156123931478>🔸</emoji> <code>{prefix + command}</code>\n"
            f"    ╰ {module.command_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in module.command_handlers
        )
        inline_descriptions = "\n".join(
            f"<emoji id=5100862156123931478>🔸</emoji> <code>@{self.bot_username + ' ' + command}</code>\n"
            f"    ╰ {module.inline_handlers[command].__doc__ or 'Нет описания для команды'}"
            for command in module.inline_handlers
        )

        header = (
            f"<emoji id=5361735750968679136>🖥</emoji> <b>{module.name}</b>\n" + (
                f"<emoji id=5224695503605735506>🧑‍💻</emoji> <b>Автор:</b> <code>{module.author}</code>\n" if module.author else ""
            ) + (
                f"<emoji id=5224695503605735506>⌨️</emoji> Версия: <b>{module.version}</b>\n" if module.version else ""
            ) + (
                f"⏺ Тег: <b>{module.tag}</b>\n" if module.tag else ""
            ) + (
                f"\n<emoji id=5400093244895797589>📄</emoji> <b>Описание:</b>\n"
                f"    ╰ {module.__doc__ or 'Нет описания для модуля'}\n\n"
            )
        )

        return await utils.answer(
            message, header + command_descriptions + "\n" + inline_descriptions
        )

    async def tags_cmd(self, app: Client, message: types.Message, args: str):
        if (tag := args.split(maxsplit=1)) not in self.all_modules.tags: # type: ignore
            text = """"""

            for tag in self.all_modules.tags:
                if not tag:
                    continue
                
                text += f'Модули с тегом {tag}\n'
                for module in list(filter(lambda mod: mod.tag == tag, self.all_modules.modules)):
                    text += f'| {module.name}\n'
                    

            return await utils.answer(
                message,
                text
            )
    
