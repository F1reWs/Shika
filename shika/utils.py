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

import asyncio
import functools
import random
import string
import typing
import yaml
import os
import git
from git import *
import contextlib
import aiohttp
from types import FunctionType
from typing import Any, List, Literal, Tuple, Union
from urllib.parse import urlparse

from pyrogram.file_id import PHOTO_TYPES, FileId
from pyrogram.types import Chat, Message, User
from pyrogram import Client

from . import database


def get_full_command(message: Message) -> Union[
    Tuple[Literal[""], Literal[""], Literal[""]], Tuple[str, str, str]
]:
    """Вывести кортеж из префикса, команды и аргументов

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    message.text = str(message.text or message.caption)
    prefixes = database.db.get("shika.loader", "prefixes", ["."])

    for prefix in prefixes:
        if (
            message.text
            and len(message.text) > len(prefix)
            and message.text.startswith(prefix)
        ):
            command, *args = message.text[len(prefix):].split(maxsplit=1)
            break
    else:
        return "", "", ""

    return prefixes[0], command.lower(), args[-1] if args else ""

def get_git_hash() -> typing.Union[str, bool]:
    """
    Get current Shika git hash
    :return: Git commit hash
    """
    try:
        return git.Repo().head.commit.hexsha
    except Exception:
        return False


async def answer(
    message: Union[Message, List[Message]],
    response: Union[str, Any],
    chat_id: Union[str, int] = None,
    doc: bool = False,
    photo: bool = False,
    disable_preview: bool = False,
    **kwargs
) -> List[Message]:
    """В основном это обычный message.edit, но:
        - Если содержание сообщения будет больше лимита (4096 символов),
            то отправится несколько разделённых сообщений
        - Работает message.reply, если команду вызвал не владелец аккаунта

    Параметры:
        message (``pyrogram.types.Message`` | ``typing.List[pyrogram.types.Message]``):
            Сообщение

        response (``str`` | ``typing.Any``):
            Текст или объект которое нужно отправить

        chat_id (``str`` | ``int``, optional):
            Чат, в который нужно отправить сообщение

        doc/photo (``bool``, optional):
            Если ``True``, сообщение будет отправлено как документ/фото или по ссылке

        kwargs (``dict``, optional):
            Параметры отправки сообщения
    """
    messages: List[Message] = []

    if isinstance(message, list):
        message = message[0]

    if isinstance(response, str) and all(not arg for arg in [doc, photo]):
        outputs = [
            response[i: i + 4096]
            for i in range(0, len(response), 4096)
        ]

        if chat_id:
            messages.append(
                await message._client.send_message(
                    chat_id, outputs[0], **kwargs, disable_web_page_preview=disable_preview)
            )
        else:
            messages.append(
                await (
                    message.edit if message.outgoing
                    else message.reply
                )(outputs[0], **kwargs, disable_web_page_preview=disable_preview)
            )

        for output in outputs[1:]:
            messages.append(
                await messages[0].reply(output, **kwargs, disable_web_page_preview=disable_preview)
            )

    elif doc:
        if chat_id:
            messages.append(
                await message._client.send_document(
                    chat_id, response, **kwargs, disable_web_page_preview=disable_preview)
            )
        else:
            messages.append(
                await message.reply_document(response, **kwargs, disable_web_page_preview=disable_preview)
            )

    elif photo:
        if chat_id:
            messages.append(
                await message._client.send_photo(
                    chat_id, response, **kwargs, disable_web_page_preview=disable_preview)
            )
        else:
            messages.append(
                await message.reply_photo(response, **kwargs, disable_web_page_preview=disable_preview)
            )

    return messages

async def answer_inline(
    message: Union[Message, List[Message]],
    bot: Union[str, int],
    query: str,
    chat_id: Union[str, int] = ''
) -> None:
    """
    Параметры:
        message (``pyrogram.types.Message`` | ``typing.List[pyrogram.types.Message]``):
            Сообщение

        bot (``str`` | ``int``):
            Ник или аиди инлайн бота
        
        query (``str``):
            Параметры для инлайн бота

        chat_id (``str`` | ``int``, optional):
            Чат, в который нужно отправить результат инлайна
    """

    if isinstance(message, list):
        message = message[0]

    app: Client = message._client
    message: Message

    results = await app.get_inline_bot_results(bot, query)

    try:
       await app.send_inline_bot_result(
        chat_id or message.chat.id,
        results.query_id,
        results.results[0].id,
        reply_to_message_id=message.reply_to_top_message_id or message.reply_to_message.id or message.reply_to_message_id,
       )
    except:
        await app.send_inline_bot_result(
        chat_id or message.chat.id,
        results.query_id,
        results.results[0].id)

def run_sync(func: FunctionType, *args, **kwargs) -> asyncio.Future:
    """Запускает асинхронно нон-асинк функцию

    Параметры:
        func (``types.FunctionType``):
            Функция для запуска

        args (``list``):
            Аргументы к функции

        kwargs (``dict``):
            Параметры к функции
    """
    return asyncio.get_event_loop().run_in_executor(
        None, functools.partial(
            func, *args, **kwargs)
    )


def get_message_media(message: Message) -> Union[str, None]:
    """Получить медиа с сообщения, если есть

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    return getattr(message, message.media or "", None)


def get_media_ext(message: Message) -> Union[str, None]:
    """Получить расширение файла

    Параметры:
        message (``pyrogram.types.Message``):
            Сообщение
    """
    if not (media := get_message_media(message)):
        return None

    media_mime_type = getattr(media, "mime_type", "")
    extension = message._client.mimetypes.guess_extension(media_mime_type)

    if not extension:
        extension = ".unknown"
        file_type = FileId.decode(
            media.file_id).file_type

        if file_type in PHOTO_TYPES:
            extension = ".jpg"

    return extension


def get_display_name(entity: Union[User, Chat]) -> str:
    """Получить отображаемое имя

    Параметры:
        entity (``pyrogram.types.User`` | ``pyrogram.types.Chat``):
            Сущность, для которой нужно получить отображаемое имя
    """
    return getattr(entity, "title", None) or (
        entity.first_name or "" + (
            " " + entity.last_name
            if entity.last_name else ""
        )
    )

def get_ram() -> float:
    """Возвращает данные о памяти."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem = process.memory_info()[0] / 2.0**20
        for child in process.children(recursive=True):
            mem += child.memory_info()[0] / 2.0**20
        return round(mem, 1)
    except:
        return 0

def get_cpu() -> float:
    """Возвращает данные о процессоре."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        cpu = process.cpu_percent()
        for child in process.children(recursive=True):
            cpu += child.cpu_percent()
        return round(cpu, 1)
    except:
        return 0
    
def get_platform() -> str:
    """Возращает платформу."""
    IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "")
    IS_CODESPACES = "CODESPACES" in os.environ
    IS_DOCKER = "DOCKER" in os.environ
    IS_GOORM = "GOORM" in os.environ
    IS_WIN = "WINDIR" in os.environ
    IS_WSL = False
    
    with contextlib.suppress(Exception):
        from platform import uname
        if "microsoft-standard" in uname().release:
            IS_WSL = True

    if IS_TERMUX:
        platform = "<emoji id=5407025283456835913>📱</emoji> Termux"
    elif IS_DOCKER:
        platform = "<emoji id=5431815452437257407>🐳</emoji> Docker"
    elif IS_GOORM:
        platform = "<emoji id=5215584860063669771>💚</emoji> Goorm"
    elif IS_WSL:
        platform = "<emoji id=6327609909416298142>🧱</emoji> WSL"
    elif IS_WIN:
        platform = "<emoji id=5309880373126113150>💻</emoji> Windows"
    elif IS_CODESPACES:
        platform = "<emoji id=5467643451145199431>👨‍💻</emoji> Github Codespaces"
    else:
        platform = "🖥️ VDS"
    
    return platform

def ascii_face() -> str:
    """
    Returnes cute ASCII-art face
    :return: ASCII-art face
    """
    return random.choice(
            [
                "ヽ(๑◠ܫ◠๑)ﾉ",
                "(◕ᴥ◕ʋ)",
                "ᕙ(`▽´)ᕗ",
                "(✿◠‿◠)",
                "(▰˘◡˘▰)",
                "(˵ ͡° ͜ʖ ͡°˵)",
                "ʕっ•ᴥ•ʔっ",
                "( ͡° ᴥ ͡°)",
                "(๑•́ ヮ •̀๑)",
                "٩(^‿^)۶",
                "(っˆڡˆς)",
                "ψ(｀∇´)ψ",
                "⊙ω⊙",
                "٩(^ᴗ^)۶",
                "(´・ω・)っ由",
                "( ͡~ ͜ʖ ͡°)",
                "✧♡(◕‿◕✿)",
                "โ๏௰๏ใ ื",
                "∩｡• ᵕ •｡∩ ♡",
                "(♡´౪`♡)",
                "(◍＞◡＜◍)⋈。✧♡",
                "╰(✿´⌣`✿)╯♡",
                "ʕ•ᴥ•ʔ",
                "ᶘ ◕ᴥ◕ᶅ",
                "▼・ᴥ・▼",
                "ฅ^•ﻌ•^ฅ",
                "(΄◞ิ౪◟ิ‵)",
                "٩(^ᴗ^)۶",
                "ᕴｰᴥｰᕵ",
                "ʕ￫ᴥ￩ʔ",
                "ʕᵕᴥᵕʔ",
                "ʕᵒᴥᵒʔ",
                "ᵔᴥᵔ",
                "(✿╹◡╹)",
                "(๑￫ܫ￩)",
                "ʕ·ᴥ·　ʔ",
                "(ﾉ≧ڡ≦)",
                "(≖ᴗ≖✿)",
                "（〜^∇^ )〜",
                "( ﾉ･ｪ･ )ﾉ",
                "~( ˘▾˘~)",
                "(〜^∇^)〜",
                "ヽ(^ᴗ^ヽ)",
                "(´･ω･`)",
                "₍ᐢ•ﻌ•ᐢ₎*･ﾟ｡",
                "(。・・)_且",
                "(=｀ω´=)",
                "(*•‿•*)",
                "(*ﾟ∀ﾟ*)",
                "(☉⋆‿⋆☉)",
                "ɷ◡ɷ",
                "ʘ‿ʘ",
                "(。-ω-)ﾉ",
                "( ･ω･)ﾉ",
                "(=ﾟωﾟ)ﾉ",
                "(・ε・`*) …",
                "ʕっ•ᴥ•ʔっ",
                "(*˘︶˘*)",
            ]
        )
    )


def random_id(size: int = 10) -> str:
    """Возвращает рандомный идентификатор заданной длины

    Параметры:
        size (``int``, optional):
            Длина идентификатора
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(size)
    )

def get_git_info() -> typing.Tuple[str, str]:
    """
    Get git info
    :return: Git info
    """
    hash_ = get_git_hash()
    return (
        hash_,
        f"https://github.com/F1reWs/Shika/commit/{hash_}" if hash_ else "",
    )

def get_commit_url() -> str:
    """
    Get current Shika git commit url
    :return: Git commit url
    """
    try:
        hash_ = get_git_hash()
        return (
            f'<a href="https://github.com/F1reWs/Shika/commit/{hash_}">#{hash_[:7]}</a>'
        )
    except Exception:
        return "Unknown"
