import asyncio

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data import config
from loader import db


class Allowed(BoundFilter):
    async def check(self, message: types.Message):
        try:
            id_new=message.from_user.id
            one=await db.select_user(id=id_new)
            id=int(one['id'])
            return id_new==id
        except:
            pass





class Admin(BoundFilter):
    async def check(self,message:types.Message):
        for one in config.admins:
            return message.from_user.id ==one
