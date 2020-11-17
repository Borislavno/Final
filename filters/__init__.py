from aiogram import Dispatcher
from filters.refeeraal import Allowed,Admin


def setup(dp: Dispatcher):
    # dp.filters_factory.bind(Allowed)
    dp.filters_factory.bind(Admin)
