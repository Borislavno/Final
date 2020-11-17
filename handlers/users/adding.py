from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asyncpg import UniqueViolationError

from filters import Admin
from loader import dp, com


@dp.message_handler(Admin(),Command('adding'))
async def confirm(message:types.message):
    await message.answer('При подтверждении действия необходимо полностью вбить необходимую'
                         ' информацию для добавлении в БД. В противном случае будет введено неправильные данные',
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [
                                     InlineKeyboardButton(text='Продолжить',callback_data='begin')
                                 ],
                                 [
                                     InlineKeyboardButton(text='Отменить',callback_data='cancel')
                                 ]
                             ]
                         )
                         )

@dp.callback_query_handler(text='cancel')
async def cancel(call: CallbackQuery):
    await call.answer(cache_time=60)
    await call.message.answer('Вы отменили операцию. \n'
                              'Для повторного действия нажмите \n'
                              '/adding')
    await call.message.edit_reply_markup(reply_markup=None)





@dp.callback_query_handler(text='begin')
async def add_new_item(call: types.callback_query, state: FSMContext):
    await call.message.answer('Давай добавим продукт. \n'
                         'План будет таков : \n'
                         '1)ID товара \n'
                         '2)Название \n'
                         '3)Описание \n'
                         '4)Цена \n'
                         '5)Изображение товара(в виде ссылки)')
    await call.message.answer('Введи ID товара в числовом формате XXXXX')
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state('id')

@dp.message_handler(state='id')
async def add_name(message: types.Message, state: FSMContext):
    id=message.text
    await state.update_data(id=id)
    await message.answer('Теперь напиши название товара')
    await state.set_state('name')


@dp.message_handler(state='name')
async def add_description(message: types.Message, state: FSMContext):
    name=message.text
    await state.update_data(name=name)
    await message.answer('Отправь описание товара БОЛЬШИМИ БУКВАМИ  \n'
                         'Так проще будет боту искать через инлайн режим')
    await state.set_state('description')


@dp.message_handler(state='description')
async def add_price(message: types.Message, state: FSMContext):
    description=message.text
    await state.update_data(description=description)
    await message.answer('Еще чуть чуть! Отправь цену товара')
    await state.set_state('price')


@dp.message_handler(state='price')
async def add_photo(message: types.Message, state:FSMContext):
    price=message.text
    await state.update_data(price=price)
    await message.answer('Отправь ссылку на фотографию, так как я не храню сами фотографии в БД')
    await state.set_state('photo')


@dp.message_handler(state='photo')
async def finish(message: types.Message, state: FSMContext):

    try:
        photo = message.text
        data = await state.get_data()
        id = int(data.get('id'))
        name = data.get('name')
        description = data.get('description')
        price = int(data.get('price'))
        print(id, name, description, price, photo)
        await com.add_item(id=id,name=name,description=description,price=price,photo=photo)
        text = f'{name} добавлен в БД! Поздравляю!'
        await message.answer_photo(photo=photo,
                                reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Посмотреть в инлайн режиме', switch_inline_query_current_chat=f'{id}')
                ]
            ]
        ))
        await state.finish()

    except ValueError:
        await message.answer('Вы ввели неправильные данные для добавления в БД')
        await state.finish()

    except UniqueViolationError:
        await message.answer(f'Ключ {id} уже существует')
        await state.finish()

    except:
        await message.answer('Что-то пошло не так...ты уверен что вводил правильные значения? \n'
                             'Попробуй снова.')
        await state.finish()

