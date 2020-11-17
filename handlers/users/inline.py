from aiogram import types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton


from loader import dp, com


def inline_to_bot(id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Купить', switch_inline_query_current_chat=f"{id}")
        ]
    ])
    return keyboard


@dp.inline_handler()
async def search(query: types.InlineQuery):
    searching = query.query
    print(0,searching)
    if len(searching)>0:
        try:
            id = int(searching)
            print(2, id)
            found = await com.one_item(id=id)
            print(3, found)
            item_id = found['id']
            await query.answer(
                results=[],
                switch_pm_text='Перейти к покупке',
                switch_pm_parameter=item_id)
        except:
            pass
        try:
            new = searching.upper()
            sorting = await com.like(new)
            print(1, sorting)
            results = []
            for one in sorting:
                results.append(
                    InlineQueryResultArticle(
                        id=one['id'],
                        title=one['name'],
                        thumb_url=one['photo'],
                        description=f'Цена: {one["price"]} рублей',
                        input_message_content=InputTextMessageContent(
                            message_text=f"Вы выбрали {one['name']}"
                        ),
                        reply_markup=inline_to_bot(id=one['id'])
                    ))
            await query.answer(results=results)
        except:
            pass
    if searching=='':
        go = await com.sort()
        results = []
        for all in go:
            print(3, all['name'])
            results.append(
                InlineQueryResultArticle(
                    id=all['id'],
                    title=all['name'],
                    thumb_url=all['photo'],
                    description=f'Цена: {all["price"]} рублей',
                    input_message_content=InputTextMessageContent(
                        message_text=f"Вы выбрали {all['name']}"
                    ),
                    reply_markup=inline_to_bot(id=all['id'])
                ))
        await query.answer(results=results)

