import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.markdown import hlink, hcode

from data import config
from filters import Allowed
from keyboards.inline.buying import buy_keyboard
from loader import dp, db, com, op
from utils.misc.qiwi import Payment, NoPaymentFound, NotEnoughMoney

@dp.message_handler(CommandStart,Allowed())
async def begin(message: types.Message, state: FSMContext):
    yo = message.get_args()
    print(yo)
    try:
        if len(yo) == 5:
            item_id = int(yo)
            product = await com.one_item(id=item_id)
            text = f"Вы выбрали {product['name']}! Хороший выбор"
            photo = product['photo']
            await message.answer_photo(photo=photo, caption=text, reply_markup=buy_keyboard(item_id=item_id))
            await state.update_data(id=item_id)
        else:
            one = await db.select_user(id=message.from_user.id)
            for param in one:
                balance = one['balance']
            bot_user = await dp.bot.get_me()
            deep_link = f"http://t.me/{bot_user.username}?start={message.from_user.id}"
            await message.answer(f'Привет {message.from_user.first_name}! \n'
                             f'Твой Баланс составляет : {balance} Рублей \n'
                             f'Пригласи друга с помощью ссылки и получи скидку 10$ на следующую покупку:\n'
                             f'{deep_link}',
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(text='Перейти к покупке',
                                                              switch_inline_query_current_chat='')
                                     ]
                                 ]
                             ))
    except:
        pass


@dp.message_handler(CommandStart)
async def bot_start(message: types.Message, state: FSMContext):
    yo=message.get_args()
    try:
        id = message.from_user.id
        referal = int(yo)
        try:
            # config.allowed_user.append(id)
            await db.add_user(id=id,name=message.from_user.full_name,
                                  balance=0, referal=referal)

            friend = await db.select_user(id=referal)
            summa = int(friend['balance'])
            new = summa + 760
            await db.update_balance(balance=new, id=referal)
        except:
            pass
        await message.answer('Вы добавлены в базу данных \n'
                                     'Для продолжения нажмите \n'
                                     '\n'
                                     '/start')
        await state.finish()


    except:
        await message.answer(f'Привет {message.from_user.full_name}! \n'
                         f'Бот работает только по приглашениям или коду \n'
                         f'Введите код :')
        await state.set_state('code')




@dp.message_handler(state='code')
async def invite(message: types.Message, state: FSMContext):
    message.text = message.text
    yo = message.get_args()
    if len(yo)==9:
        id = message.from_user.id
        referal = int(yo)
        await db.add_user(id=id, name=message.from_user.full_name,
                          balance=0, referal=referal)
        friend = await db.select_user(id=referal)
        summa = int(friend['balance'])
        new = summa + 760
        await db.update_balance(balance=new, id=referal)
        await message.answer('Вы добавлены в базу данных \n'
                             'Для продолжения нажмите \n'
                             '\n'
                             '/start')
        await state.finish()
    if len(yo) =='':
        try:
            referal = int(message.text)
            search = await db.one_user(id=referal)
            await db.add_user(id=message.from_user.id,name=message.from_user.full_name, balance=0, referal=referal)
            friend = await db.one_user(id=referal)
            summa = int(friend['balance'])
            new = summa + 760
            await db.update_balance(balance=new, id=referal)
            await message.answer('Вы добавлены в базу данных! Для продолжения нажмите : \n'
                                 '/start')
            await state.finish()
        except ValueError:
            await message.answer('Вы не добавлены в базу данных! Попробуйте позже')
            await state.finish()


@dp.callback_query_handler(text_contains="buy")
async def pre_buy(call:CallbackQuery,state: FSMContext):
    id=await db.select_user(id=call.from_user.id)
    for param in id:
        balance=int(id['balance'])
    await state.update_data(balance=balance)
    item_id = int(call.data.split(":")[-1])
    await state.update_data(item_id=item_id)
    if balance==0:
        await call.answer(cache_time=5)
        await call.message.answer('У вас нет бонусных рублей',reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Продолжить покупку', callback_data='end')
                ]
            ]
        ))
        await state.set_state('choice')
    else:
        await call.answer(cache_time=5)
        await call.message.answer(f'У вас есть {balance} бонусных рублей. Вы можете использовать их'
                                  ,reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Использовать',callback_data='use')
                    ],
                    [
                        InlineKeyboardButton(text='Продолжить покупку',callback_data="end")
                    ]
                ]
            ))
        await state.set_state('choice')

@dp.callback_query_handler(text_contains='use',state='choice')
async def bonus(call: CallbackQuery,state: FSMContext):
    await call.message.answer('Напишите сколько бонусных рублей вы хотите использовать')
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state('bonus')


@dp.message_handler(state='bonus')
async def konv(message: types.Message, state: FSMContext):
    sum=message.text
    try:
        sum=int(sum)
        data=await state.get_data()
        balance=data.get('balance')
        item_id=int(data.get('item_id'))
        item= await com.one_item(id=item_id)

        if sum> balance:
            await message.answer('У нас недостаточно скидочных рублей для покупки, введите сумму поменьше')
            return
        if sum<=balance:
            if sum == item['price']:
                sum=sum-1
            new_balance=balance-sum
            await message.answer('Отлично! Продолжим покупку',reply_markup=
                                     InlineKeyboardMarkup(
                                         inline_keyboard=[
                                             [
                                                 InlineKeyboardButton('Продолжить',callback_data='end')
                                             ]
                                         ]
                                     ))
            await db.update_balance(balance=new_balance,id=message.from_user.id)
            await state.update_data(bonus=sum)
            await state.set_state('choice')
    except ValueError:
            await message.answer('Что-то пошло не так. Введите сумму, которую хотите использовать',reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Продолжить без бонусов',callback_data='end')
                ],
                [
                    InlineKeyboardButton(text='Отменить',callback_data='cancel')
                ]
            ]))
            return



@dp.callback_query_handler(text="end", state='choice')
async def pre_finish(call:CallbackQuery,state: FSMContext):
    data = await state.get_data()
    item_id = data.get('item_id')
    item = await com.one_item(id=item_id)
    try:
        price = int(item['price'])
    except TypeError:
        await call.message.answer("Что-то пошло не так😞 \n", reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='Выбери товар', switch_inline_query_current_chat='')
                    ]
                ]
            ))
        await state.finish()
    except:
        pass
    try:
        bonus = int(data.get('bonus'))
    except:
        pass
    try:
        price = price - bonus
    except:
        pass
    amount = price

    payment = Payment(amount=amount)
    payment.create()
    await state.update_data(payment=payment)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Последний шаг',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Купить",
                                url=payment.invoice
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text='Оплачено',
                                callback_data='paid'
                            ),
                            InlineKeyboardButton(
                                text="Отмена",
                                callback_data="cancel")
                        ],
                    ]))



@dp.callback_query_handler(text='cancel',state='choice')
async def exp(call:CallbackQuery,state: FSMContext):
    try:
        data=await state.get_data()
        balance=data.get('balance')
        await db.update_balance(balance=balance,id=call.from_user.id)
    except:
        pass

    await call.message.answer('Вы отменили покупку \n'
                              'Нажмите кнопку чтобы выбрать товары',
                              reply_markup=InlineKeyboardMarkup(
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Выбрать товары',switch_inline_query_current_chat="")
                                      ]
                                  ]
                              ))
    await state.finish()




@dp.callback_query_handler(text="paid", state='choice')
async def approve_payment(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment: Payment = data.get("payment")
    try:
        payment.check_payment()
    except NoPaymentFound:
        await call.message.answer("Транзакция не найдена.",reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Повторить',callback_data='paid')
                ]
            ]
        ))
        return
    except NotEnoughMoney:
        await call.message.answer("Оплаченная сума меньше необходимой.",reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Повторить',callback_data='paid')
                ]
            ]
        ))
        return

    else:
        item_id = int(data.get('id'))
        id_zakaz=random.randrange(100000)
        await op.add_zakaz(id_zakaz=id_zakaz,id_user=call.from_user.id,
                           name_user=call.from_user.first_name,id_item=item_id,status='created')
        await call.message.answer("Успешно оплачено \n"
                                  f"Номер заказа: {id_zakaz}")
    await call.message.edit_reply_markup()
    await state.finish()



