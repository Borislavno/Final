import asyncio
import random

from data import config
from utils.db_api.sklad import Sklad
from utils.db_api.baza_ludi import Database
from utils.db_api.zakaz import Zakaz


async def test():

    sort= await op.sort()
    for a in sort:
        print(a['name'])







loop = asyncio.get_event_loop()
op = loop.run_until_complete(Sklad.create())
aa=loop.run_until_complete(Zakaz.create())
loop.run_until_complete(test())

