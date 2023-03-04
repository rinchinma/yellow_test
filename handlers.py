from aiogram import types, Dispatcher

from create_bot import bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message

from models import CustomUser
from modules import FunctionModule

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


def keyboard_client():
    button_1 = KeyboardButton('❓Мой профиль')
    button_2 = KeyboardButton('💸Имитация сделки')
    button_3 = KeyboardButton('👥Мои рефералы')

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(button_1).row(button_2, button_3)
    return keyboard


async def start(message: types.Message):

    module = FunctionModule()
    module.startReferral(message)

    await bot.send_message(message.from_user.id, 'Добро пожаловать, {name},'.format(
        name=message.from_user.username
    ), reply_markup=keyboard_client())


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(start, text='start', state=None)


"""___________________________________________________________________________________________________"""


async def my_profile(message: types.Message):
    query = CustomUser.get(user_id=message.from_user.id)
    user = CustomUser.get(id=query)

    if user.invited_id != 0:
        invited = user.invited_id
    else:
        invited = 'Перешли не по реферальной ссылке'

    text = '*Ваша партнёрская статистика*\n\nВаш баланс: {balance} $ \n' \
           '\nВаша реферальная ссылка: {link}\n\n' \
           'Вас пригласил: {invited}'.format(
            balance=round(user.balance, 2), link=user.referral_link, invited=invited, parse_mode="Markdown")
    await message.answer(text)


def register_handlers_my_profile(dp: Dispatcher):
    dp.register_message_handler(my_profile, commands=['/❓Мой профиль'])
    dp.register_message_handler(my_profile, text='❓Мой профиль', state=None)


"""___________________________________________________________________________________________________"""


async def my_referrals(message: types.Message):
    query = CustomUser.get(user_id=message.from_user.id)
    user = CustomUser.get(id=query)
    module = FunctionModule()
    if user.followed_ref_link != '':
        level_one, level_two, level_three, level_four, level_five = module.getMyReferrals(user.followed_ref_link)

        text = '*Ваш список привеченных партнеров:*\n' \
               '*Партнеры 1 уровня:* {people1} чел.\n{count_people1}' \
               '\n*Партнеры 2 уровня:* {people2} чел.\n{count_people2}' \
               '\n*Партнеры 3 уровня:* {people3} чел.\n{count_people3}' \
               '\n*Партнеры 4 уровня:* {people4} чел.\n{count_people4}' \
               '\n*Партнеры 5 уровня:* {people5} чел.\n{count_people5}'.format(
                count_people1=level_one, people1=len(level_one.split(' ')),
                count_people2=level_two, people2=len(level_two.split(' ')),
                count_people3=level_three, people3=len(level_three.split(' ')),
                count_people4=level_four, people4=len(level_four.split(' ')),
                count_people5=level_five, people5=len(level_five.split(' ')), parse_mode="Markdown")

        await message.answer(text)
    else:
        await message.answer('Вы еще никого не пригласили!')


def register_handlers_my_referrals(dp: Dispatcher):
    dp.register_message_handler(my_referrals, commands=['/👥Мои рефералы'])
    dp.register_message_handler(my_referrals, text='👥Мои рефералы', state=None)


"""___________________________________________________________________________________________________"""


class AddStates(StatesGroup):
    stage_one = State()


async def get_stage_one(message: Message, state=FSMContext):
    await message.answer(
        'Отправьте сумму сделки в цифрах\n'
        'После этого пользователям, которые отправили вам реферальную ссылку, стоит проверить баланс')
    await AddStates.next()


async def get_stage_two(message: Message, state=FSMContext):
    query = CustomUser.get(user_id=message.from_user.id)
    user = CustomUser.get(id=query)

    module = FunctionModule()
    if user.invited_id != 0:
        await message.answer(user.invited_id)
        for_message_list = module.payReferrer(user.invited_id, int(message.text))

        for user_id in for_message_list:
            if user_id != 0:
                await bot.send_message(int(user_id), 'Поступила выплата процентов по партнерской программе!\n'
                                                     'Проверьте баланс!')
    else:
        await message.answer('Вас никто не рефералил - по сему нет смысла тестить\n'
                             'Попробуйте затестить через зарефераленный аккаунт')
    await state.finish()


def register_handlers_deal(dp: Dispatcher):
    dp.register_message_handler(get_stage_one, commands=['/💸Имитация сделки'])
    dp.register_message_handler(get_stage_one, text='💸Имитация сделки', state=None)

    dp.register_message_handler(get_stage_two, state=AddStates.stage_one)
