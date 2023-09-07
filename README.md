<p align="center">
    </a>
    <img alt="Telegram" width="500px" src="https://api.f1rew.me/file/shika_logo.jpg">
    <br>
    <b>ShikaUB v1.0.0</b>
    <br>
    <b>Telegram userbot</b>
<br><br>

</p>
<hr>

[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=The+best+telegram+userbot.)](https://t.me/shikaub)
<hr>

<h1>Установка</h1>
- Termux (Скачать термукс можно по <a href="https://f-droid.org/repo/com.termux_118.apk">этой ссылке</a>)<br>⚠️ Версия с PlayStore не работает!

```
pkg update -y && pkg install python3 -y && pkg install python3-pip -y && pkg install git -y && pkg install libjpeg-turbo -y && git clone https://github.com/F1reWs/Shika && cd Shika && pip3 install -r requirements.txt && bash start.sh
```

- APT (Debian/Ubuntu based)

```
apt update -y && apt upgrade -y && apt install python3-pip -y && apt install git -y && git clone https://github.com/F1reWs/Shika && cd Shika && pip3 install -r requirements.txt && bash start.sh
```

- Pacman (Arch based)

```
sudo pacman -Syu python-pip git && git clone https://github.com/F1reWs/Shika && cd Shika && pip3 install -r requirements.txt && bash start.sh
```


- Mac OS

Установи <a href="https://www.python.org/downloads/">Python 3.9+</a>

Скачай и разархивируй <a href="https://github.com/F1reWs/Shika/archive/refs/heads/main.zip">этот файл</a>

Напиши в терминале `pip install -r requirements.txt`

<h4>Что бы включить Shika</h3>

Напиши в терминале `python3 -m shika`
<hr>

<h1>Авторизация</h1>
В Shika авторизация, <b>быстрая</b> и <b>лёгкая</b>
<table>
   <img src="https://api.f1rew.me/file/shika_install.gif" height="400" align="middle">
</table>

<h1>Модули</h1>

> Модули для Shika, ты можешь найти по <a href="https://t.me/shika_chat/12">этой ссылке</a>

<h2>Пример модуля</h2>

> Больше примеров функций и полное описание смотри в файле <a href="./shika/modules/_example.py">_example.py</a>

<pre lang="python">
from pyrogram import Client, types
from .. import loader, utils


@loader.module(name="Example", author="F1reW", version=1.0)
class ExampleMod(loader.Module):
    """Описание модуля"""

    async def example_cmd(self, app: Client, message: types.Message):
        """Описание команды"""
        return await utils.answer(
            message, "Пример команды")

    @loader.on(lambda _, __, m: m and m.text == "Привет, это проверка вотчера")
    async def watcher(self, app: Client, message: types.Message):
        return await message.reply(
            "Привет, все работает отлично")
</pre>

<hr>
<h1>Канал и чат</h1>
<a href="https://t.me/shikaub">
<img alt="Telegram" src="https://img.shields.io/badge/Telegram_Channel-0a0a0a?style=for-the-badge&logo=telegram">
</a>
<a href="https://t.me/shika_chat">
<img alt="Telegram" src="https://img.shields.io/badge/Telegram_Chat-0a0a0a?style=for-the-badge&logo=telegram">
</a>
<br>
<hr>
<i>⚠️ Этот проект предоставляется «как есть». Разработчик не несет НИКАКОЙ ответственности за любые проблемы, вызванные пользовательским ботом. Устанавливая Shika, вы берете на себя все риски. Пожалуйста, прочтите https://core.telegram.org/api/terms для получения дополнительной информации.</i>
<br>
<hr> 
