from aiogram import Router, html, types, F

from dragonpottery_bot.application.app_state import app_state

router = Router(name=__name__)


@router.message(F.contact.user_id == F.from_user.id)
async def contact_message_handler(message: types.Message) -> None:
    assert message.contact
    sum_by_contact = await app_state.order_repository.get_sum_by_contact()

    if message.contact.phone_number not in sum_by_contact:
        answer = 'Вы не совершали покупок ранее'
    else:
        orders_sum = sum_by_contact[message.contact.phone_number]
        answer = f'Вы совершили покупки на {orders_sum} ₽'
        promocode, percent = await app_state.order_repository.calc_discount(orders_sum)
        if promocode:
            answer += f'\nВаш промокод {html.code(promocode)} на скидку {percent}%'
            await app_state.order_repository.save_issue(message.contact.phone_number, orders_sum, promocode)
    await message.answer(
        answer,
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(F.from_user)
async def default_handler(message: types.Message) -> None:
    assert message.from_user
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=[[
            types.KeyboardButton(text='Отправить номер телефона', request_contact=True),
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        f'Здравствуйте, {html.bold(message.from_user.full_name)}! '
        f'Отправьте ваш номер телефона с помощью кнопки "Отправить номер телефона".',
        reply_markup=reply_markup,
    )
