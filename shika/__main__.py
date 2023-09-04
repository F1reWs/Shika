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

import sys

from . import main

if sys.version_info < (3, 9, 0):
    print("Требуется Python 3.9 или выше")
    sys.exit(1)


from argparse import ArgumentParser
import asyncio


def parse_arguments():
    parser = ArgumentParser(
        prog="shika", description="Юзербот",
        add_help=False
    )

if __name__ == "__main__":
    asyncio.run(main.main())
