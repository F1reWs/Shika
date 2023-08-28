import configparser
import logging
import sys
import os

import base64
import asyncio

from colorama import Fore, Style
from datetime import datetime
from getpass import getpass
from typing import NoReturn, Tuple, Union

from pyrogram import Client, errors, types, raw
from pyrogram.session.session import Session
from pyrogram.raw.functions.auth.export_login_token import ExportLoginToken

from qrcode.main import QRCode


from . import __version__

Session.notice_displayed: bool = True


def colored_input(prompt: str = "", hide: bool = False) -> str:
    """Цветной инпут"""
    frame = sys._getframe(1)
    return (input if not hide else getpass)(
        "\x1b[32m{time:%Y-%m-%d %H:%M:%S}\x1b[0m | "
        "\x1b[1m{level: <8}\x1b[0m | "
        "\x1b[36m{name}\x1b[0m:\x1b[36m{function}\x1b[0m:\x1b[36m{line}\x1b[0m - \x1b[1m{prompt}\x1b[0m".format(
            time=datetime.now(), level="INPUT", name=frame.f_globals["__name__"],
            function=frame.f_code.co_name, line=frame.f_lineno, prompt=prompt
        )
    )


class Auth:
    """Авторизация в аккаунт"""

    def __init__(self, session_name: str = "../teagram") -> None:
        self._check_api_tokens()

        config = configparser.ConfigParser()
        config.read("./config.ini")

        self.app = Client(
            name=session_name, api_id=config.get('pyrogram', 'api_id'),
            api_hash=config.get('pyrogram', 'api_hash'),
            app_version=f"v{__version__}"
        )

    def _check_api_tokens(self) -> bool:
        """Проверит установлены ли токены, если нет, то начинает установку"""

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\033[96m" + f"""
               .::---------::.               
           :---------------------:           
        .---------------------------:        
      :-------------------------------:      
    .-----------------------------------.    
   :-------------------------------------:   
  :----------------------------------------  
 :--------------------------:...-----------: 
.----------------------:..      :-----------.
:-----------------::.           ------------:
--------------:.       .::      -------------
----------..        .:-:       :-------------
----------:..    .:--.         --------------
.------------------:           -------------:
 -------------------:.        :------------- 
 .---------------------:.     -------------. 
  .-----------------------:..:------------.  
    -------------------------------------.   
     :---------------------------------:     
       :-----------------------------:       
         .:-----------------------:.         
            .::---------------::.            

     ______   __        _   __              
   .' ____ \ [  |      (_) [  |  _          
   | (___ \_| | |--.   __   | | / ]  ,--.   
    _.____`.  | .-. | [  |  | '' <  `'_\ :  
   | \____) | | | | |  | |  | |`\ \ // | |, 
    \______.'[___]|__][___][__|  \_]\'-;__/ 

{Fore.CYAN + Style.BRIGHT}Добро пожаловать в Shika!{Style.RESET_ALL}
"""+ "\033[0m")

        config = configparser.ConfigParser()
        if not config.read("./config.ini"):
            enter_api_data = input(f"{Fore.CYAN + Style.BRIGHT}Использовать стандартные API id и Api hash? [y/n]{Style.RESET_ALL} ")
            if enter_api_data == "y":
                config["pyrogram"] = {
                "api_id": "2040",
                "api_hash": "b18441a1ff607e10a989891a5462e627",
            }
                
            else:
              print(f"""
1. Откройте {Fore.CYAN}https://my.telegram.org{Style.RESET_ALL} и войдите в свой аккаунт.
2. Нажмите на инструменты разработки API.
3. Создайте новое приложение, введя необходимые данные.
4. Скопируйте ваш {Fore.CYAN}API id{Style.RESET_ALL} и {Fore.CYAN}API hash{Style.RESET_ALL}.
""")
              config["pyrogram"] = {
                "api_id": input(f"{Fore.CYAN + Style.BRIGHT}Введи свой API id:{Style.RESET_ALL} "),
                "api_hash": input(f"{Fore.CYAN + Style.BRIGHT}Введи API hash:{Style.RESET_ALL} ")
            }

              with open("./config.ini", "w") as file:
                config.write(file)

            with open("./config.ini", "w") as file:
                config.write(file)
        
        return True

    async def send_code(self) -> Tuple[str, str]:
        """Отправить код подтверждения"""
        while True:
            error_text: str = ""

            try:
                phone = input(f"{Fore.CYAN + Style.BRIGHT}Введи номер телефона:{Style.RESET_ALL} ")
                return phone, (await self.app.send_code(phone)).phone_code_hash
            except errors.PhoneNumberInvalid:
                error_text = "Неверный номер телефона, попробуй ещё раз"
            except errors.PhoneNumberBanned:
                error_text = "Номер телефона заблокирован"
            except errors.PhoneNumberFlood:
                error_text = "На номере телефона флудвейт"
            except errors.PhoneNumberUnoccupied:
                error_text = "Номер не зарегистрирован"
            except errors.BadRequest as error:
                error_text = f"Произошла неизвестная ошибка: {error}"

            if error_text:
                print(f"{Fore.RED}{error_text}{Style.RESET_ALL}")

    async def enter_code(self, phone: str, phone_code_hash: str) -> Union[types.User, bool]:
        """Ввести код подтверждения"""
        try:
            code = input(f"{Fore.CYAN + Style.BRIGHT}Введи код:{Style.RESET_ALL} ")
            
            return await self.app.sign_in(phone, phone_code_hash, code)
        except errors.SessionPasswordNeeded:
            return False

    async def enter_2fa(self) -> types.User:
        """Ввести код двухфакторной аутентификации"""
        while True:
            try:
                passwd = input(f"{Fore.CYAN + Style.BRIGHT}Введи пароль от 2FA:{Style.RESET_ALL} ")

                return await self.app.check_password(passwd)
            except errors.BadRequest:
                print(f"{Fore.RED}Неверный пароль! Попробуй снова{Style.RESET_ALL}")

    async def authorize(self) -> Union[Tuple[types.User, Client], NoReturn]:
        """Процесс авторизации в аккаунт"""
        await self.app.connect()

        try:
            me = await self.app.get_me()
        except errors.AuthKeyUnregistered:
            config = configparser.ConfigParser()
            config.read('config.ini')

            qr = input(f"{Fore.CYAN + Style.BRIGHT}Вход по QRcode? [y/n]{Style.RESET_ALL} ")

            if qr[0] == "y":
                api_id = int(config.get("pyrogram","api_id"))
                api_hash = config.get("pyrogram","api_hash")

                tries = 0
                while True:                    
                    try:
                        r = await self.app.invoke(
                            ExportLoginToken(
                                api_id=api_id, api_hash=api_hash, except_ids=[]
                            )
                        )
                    except errors.exceptions.unauthorized_401.SessionPasswordNeeded:
                        me: types.User = await self.enter_2fa()
                        
                        break

                    if isinstance(r, raw.types.auth.login_token_success.LoginTokenSuccess):
                        break
                    if isinstance(r, raw.types.auth.login_token.LoginToken) and tries % 30 == 0:
                        qr = QRCode(error_correction=1)

                        qr.add_data('tg://login?token={}'.format(
                            base64.urlsafe_b64encode(r.token).decode('utf-8').rstrip('=') # type: ignore
                        ))

                        qr.make(fit=True)
                        os.system('cls' if os.name == 'nt' else 'clear')
                        qr.print_ascii()

                        print(f"{Fore.CYAN}{Style.BRIGHT}Перейдите: Настройки > Устройства > Подключить устройство{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{Style.BRIGHT}Сканируйте QR{Style.RESET_ALL}")
                    
                    tries += 1
                    await asyncio.sleep(1)

                print(f"""
{Fore.CYAN + Style.BRIGHT}Shika была успешно установлена!{Style.RESET_ALL}

Подождите немного... Мы всё настроем для удобного использование юзербота!
""")
                    
            else:
                phone, phone_code_hash = await self.send_code() # type: ignore
                logged = await self.enter_code(phone, phone_code_hash)
                if not logged:
                    me: types.User = await self.enter_2fa()
                else:          
                    me: types.User = await self.app.get_me()      
                
                print(f"""
{Fore.CYAN + Style.BRIGHT}Shika была успешно установлена!{Style.RESET_ALL}

Подождите немного... Мы всё настроем для удобного использование юзербота!
""")
                
        except errors.SessionRevoked:
            print("Сессия была сброшена, удали сессию и заново введи команду запуска")
            await self.app.disconnect()
            return sys.exit(64)

        return me, self.app