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
            msg = await app.get_messages(*map(int, restart["msg"].split(":")))
            if (
                not msg.empty
                and msg.text != (
                    restarted_text
                )
            ):
                await msg.edit(restarted_text)

        db.pop("shika.loader", "restart")

    await idle()

    logging.info("Завершение работы...")
    return True
