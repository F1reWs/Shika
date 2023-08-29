import logging
import time
import os
from colorama import Fore, Style

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
            f"✅ Перезагрузка прошла успешно! ({round(time.time())-int(restart['start'])} сек.)"
            if restart["type"] == "restart"
            else f"✅ Обновление прошло успешно! ({round(time.time())-int(restart['start'])} сек.)"
        )
        
        try:
            msg = await app.get_messages(*map(int, restart["msg"].split(":")))
            if (
                not msg.empty
                and msg.text != (
                    restarted_text
                )
            ):
                await msg.edit(restarted_text)
        except:
            print(restarted_text)

        db.pop("shika.loader", "restart")

    await idle()

    logging.info("Завершение работы...")
    return True
