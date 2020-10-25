from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from db.daily import sql_daily_exe as sql_pg

from handlers.users import dp


# TODO Вынести текст сообщейний в отдельный файл
# Вместе с Command Перехватывает сообщения типа /test
# Тестовая функция для проверки чего либо
@dp.message_handler(Command('test'))
async def show_test(msg: Message):
    await msg.answer(text='Тестовое сообщение')
    # await msg.answer(sql.check_user_subscribe_to_daily(msg.from_user.id)[0])
    await msg.answer(sql_pg.check_user_subscribe_to_daily(msg.from_user.id)[0])


# TODO Сделать проверку. Если пользователь не подписан, то перенаправлять его на команду start для того что бы он
#  попал в БД
@dp.message_handler(Command('start'))
async def process_start(msg: Message):
    user_exists = sql_pg.check_user_exists(msg.from_user.id)[0]
    if user_exists:
        await msg.answer(text=f'С возвращением {msg.from_user.first_name}.\n'
                              'Для вызова спраки введите /help')
    else:
        await msg.answer(text=f'{msg.from_user.first_name}, приятно познакомится.\n'
                              'Для вызова спраки введите /help')
        sql_pg.add_new_user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name)


@dp.message_handler(Command('help'))
async def process_start(msg: Message):
    await msg.answer(text=f' Для просмотра списка доступных подписок введите /subscriptions')


@dp.message_handler(Command('subscriptions'))
async def process_help(msg: Message):
    await msg.answer(text='/daily - Бот каждый день в заданное время будет запрашивать у вас список задач, '
                          'а в теченее дня заданное колличество раз напоминать о незавершённых делах')
