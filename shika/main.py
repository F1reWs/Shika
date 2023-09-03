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
import time
import os
from colorama import Fore, Style
import requests

from pyrogram.methods.utilities.idle import idle

from . import auth, database, loader


async def main():
    """Основной цикл юзербота"""
    me, app = await auth.Auth().authorize()
    await app.initialize()

    db = database.db
    db.init_cloud(app, me)

    modules = loader.ModulesManager(app, db, me)
    await modules.load(app)

    prefix = db.get("shika.loader", "prefixes", ["."])[0]
    #os.system('cls' if os.name == 'nt' else 'clear')

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

{Fore.CYAN + Style.BRIGHT}Shika запущена!{Style.RESET_ALL}
"""+ "\033[0m")
    
    print(f'{Fore.MAGENTA}Твой префикс - "{prefix}"{Style.RESET_ALL}')

    if (restart := db.get("shika.loader", "restart")):
      try:
        restarted_text = (
            f"<b><emoji id=6334758581832779720>✅</emoji> Shika полностью перезагружена! ({round(time.time())-int(restart['start'])} сек.)</b>"
            if restart["type"] == "restart"
            else f"<b><emoji id=6334758581832779720>✅</emoji> Shika обновлена до последней версии! ({round(time.time())-int(restart['start'])} сек.)</b>"
        )

        if restart["type"] == "update_from_bot":
            restarted_text = f"<b>✅ Shika обновлена до последней версии! ({round(time.time())-int(restart['start'])} сек.)</b>"

            token = db.get("shika.bot", "token")

            url = f'https://api.telegram.org/bot{token}/editMessageText'

            payload = {
               'chat_id': restart["msg"].split(":")[0],
               'message_id': restart["msg"].split(":")[1],
               'text': restarted_text,
               'parse_mode': "HTML",
            }
            response = requests.post(url, json=payload)     

        if not restart["type"] == "update_from_bot":
            await app.edit_message_text(
    chat_id=int(restart["msg"].split(":")[0]),
    message_id=int(restart["msg"].split(":")[1]),
    text=restarted_text
           )
            db.pop("shika.loader", "restart")
      except Exception as err:
        print(err)
        token = db.get("shika.bot", "token")
        url = f'https://api.telegram.org/bot{token}/sendMessage?'

        payload = {
               'chat_id': db.get("shika.me", "id"),
               'text': "<b>✅ Shika была успешно перезагружена!</b>\n<i>Сообщение отправлено сюда, так как Shika не смогла отредактировать сообщение в чате где она перезагружалась.</i>",
               'parse_mode': "HTML",
            }
        response = requests.post(url, json=payload)    
        db.pop("shika.loader", "restart") 

    me = await app.get_me()
    db.set("shika.me", "id", me.id)
    
    await idle()

    logging.info("Завершение работы...")
    return True
