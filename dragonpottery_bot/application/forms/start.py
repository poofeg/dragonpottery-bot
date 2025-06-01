from aiogram import Router, html, types, F
from aiogram.utils.i18n import gettext as _

from dragonpottery_bot.application.app_state import app_state

router = Router(name=__name__)


@router.message(F.contact.user_id == F.from_user.id)
async def contact_message_handler(message: types.Message) -> None:
    assert message.contact
    sum_by_contact = await app_state.order_repository.get_sum_by_contact()

    if message.contact.phone_number not in sum_by_contact:
        answer = [_("You haven't made any purchases before")]
    else:
        orders_sum = sum_by_contact[message.contact.phone_number]
        answer = [_('You have made purchases for {orders_sum} ₽').format(orders_sum=orders_sum)]
        promocode, percent = await app_state.order_repository.calc_discount(orders_sum)
        if promocode:
            answer.append(_('Your promo code is {promocode} for a {percent}%% discount').format(
                promocode=html.code(promocode), percent=percent
            ))
            await app_state.order_repository.save_issue(message.contact.phone_number, orders_sum, promocode)
    await message.answer(
        '\n'.join(answer),
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(F.from_user)
async def default_handler(message: types.Message) -> None:
    assert message.from_user
    reply_markup = types.ReplyKeyboardMarkup(
        keyboard=[[
            types.KeyboardButton(text=_('Send my phone number'), request_contact=True),
        ]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        _('Hello, {full_name}! Send your phone number using the "Send my phone number" button.').format(
            full_name=html.bold(message.from_user.full_name)
        ),
        reply_markup=reply_markup,
    )
