import time

import asyncio

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp
from utils.db_sqlite_api.sqlite import sql_exec as sql
from handlers.users.message_answer import General as General_message, Daily as Daily_message
from keyboards.inline.daily_buttons import inline_daily_function_btn, inline_daily_options_btn
from utils.user_input import number_in_range, validation_time, normalize_time_to_pattern
from utils.mailer import calculate_dispatch_time, send_daily_lists
from db.daily import sql_daily_exe as sql_pg


class Daily(StatesGroup):
    # Состояни нужные для первоночальной настрйки
    # Подписаться и задать параметры
    daily_subscribe = State()
    start_time = State()
    finish_time = State()
    how_many_time = State()
    add_first_tasks = State()
    daily_set_timezone = State()

    # Состояния нужные работы с активной подпиской
    daily = State()
    show_tasks_list = State()
    add_new_task = State()
    daily_options_start_time = State()
    daily_options_finish_time = State()
    daily_options_how_many_time = State()


@dp.message_handler(Command('test'), state='*')
async def test_function(msg: Message):
    # await msg.answer(sql.check_timezone_options(msg.from_user.id)[0] is not None)
    await msg.answer(sql_pg.check_user_subscribe_to_daily(1))


# TODO цикл срабатывает с задежкой в 60 сек. Каждую итерацию цикла вызывать асинхронную функцию рассылки
async def send_time(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        await send_daily_lists()


@dp.message_handler(Command('daily'), state="*")
async def process_daily(msg: Message):
    """
    Точка входа в подписку Daily
    Если пользователь тут первый,
    Предлагается подписаться и пройти первоначальную настройку,
    Если подписан или когда-то был подписан, то попадаем меню подписки
    """

    # Проверяем есть ли такаой пользователь в нашей БД
    # if sql.check_user_subscribe_to_daily(msg.from_user.id)[0]:
    if sql_pg.check_user_subscribe_to_daily(msg.from_user.id)[0]:
        await msg.answer(text=f'{General_message.choice_action.value}',
                         reply_markup=inline_daily_function_btn,
                         parse_mode='HTML')
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Да')
        keyboard.add('Отмена')
        await msg.answer(text='Вы хотите подписаться?', reply_markup=keyboard)
        await Daily.daily_subscribe.set()


# ##################################################################################################
# Функции для новых пользователей                                                                  #
# Добавляют пользователя в БД проводят первоночальную настройку                                    #
# ##############################################################                                   #
@dp.message_handler(state=Daily.daily_subscribe, content_types=types.ContentType.TEXT)
async def process_choice_time(msg: Message, state: FSMContext):
    """
    Пользователю предлагается выбрать время в которое он будет получать уведомления
    о том что нужно составить список дел на день
    """
    if msg.text.lower() == 'да':
        await state.update_data(subscription_status=1)
        await msg.answer(Daily_message.start_time.value, reply_markup=ReplyKeyboardRemove())
        await Daily.start_time.set()
    elif msg.text.lower() == 'отмена':
        await state.finish()
        await msg.answer(Daily_message.action_canceled.value, reply_markup=ReplyKeyboardRemove())
    else:
        await msg.answer(Daily_message.push_btn_below.value)
        return


@dp.message_handler(state=Daily.start_time, content_types=types.ContentType.TEXT)
async def process_start_time(msg: Message, state: FSMContext):
    """
    Пользователю предлагается задать время в которое он будет получать уведомлени
    что время на выполнение дел подошло к концу (Дедлайн)
    """
    # TODO придумать механизм что бы, если пользователь ввел, например время 7:15 вместо 07:15 бот его не просил
    #  ввести время по новой
    if validation_time(msg.text):
        await state.update_data(start_time=normalize_time_to_pattern(msg.text))
        await msg.answer(Daily_message.finish_time.value)
        await Daily.finish_time.set()
    else:
        await msg.answer(Daily_message.start_time.value)
        return


@dp.message_handler(state=Daily.finish_time, content_types=types.ContentType.TEXT)
async def process_how_many_time(msg: Message, state: FSMContext):
    """
    Предлагается выбрать колличество раз которое бот будет напоминать о списке дел
    """
    # if number_in_range(msg.text, -1, 24):
    if validation_time(msg.text):
        await state.update_data(finish_time=normalize_time_to_pattern(msg.text))
        await msg.answer(Daily_message.how_many_time.value)
        await Daily.how_many_time.set()
    else:
        await msg.answer(Daily_message.finish_time.value)
        return


@dp.message_handler(state=Daily.how_many_time, content_types=types.ContentType.TEXT)
async def process_daily_subscribe_finish(msg: Message, state: FSMContext):
    """
    Записываем данные полученные от пользователя в БД
    """
    if number_in_range(msg.text, -1, 11):
        await state.update_data(how_many_time=msg.text)
        user_data = await state.get_data()
        # sql.subscription_to_daily(msg.from_user.id,
        #                           user_data['start_time'],
        #                           user_data['finish_time'],
        #                           user_data['how_many_time'],
        #                           user_data['subscription_status'])
        sql_pg.subscription_to_daily(msg.from_user.id,
                                     user_data['start_time'],
                                     user_data['finish_time'],
                                     user_data['how_many_time'],
                                     user_data['subscription_status'])

        # sql.remove_mailing_list(msg.from_user.id, 1)
        sql_pg.remove_mailing_list(msg.from_user.id, 1)
        dispatch_time = calculate_dispatch_time(user_data['start_time'],
                                                user_data['finish_time'],
                                                user_data['how_many_time'])

        # sql.set_mailing_daily_list(msg.from_user.id, dispatch_time)
        print(dispatch_time)
        sql_pg.set_mailing_daily_list(msg.from_user.id, dispatch_time)
        # TODO Придумать механиз при котором пользователю будет утром предложено ввести список задач на день
        await msg.answer('Вы успешно подписались.\n'
                         f'Каждый день бот в {user_data["start_time"]} будет спрашивать у вас список дел')

        # if sql.check_timezone_options(msg.from_user.id)[0] is not None:
        if sql_pg.check_timezone_options(msg.from_user.id)[0] is not None:
            await msg.answer(Daily_message.your_first_task.value)
            await Daily.add_first_tasks.set()
        else:
            await msg.answer(General_message.set_timezone.value)
            await Daily.daily_set_timezone.set()
    else:
        await msg.answer(Daily_message.how_many_time.value)
        return


@dp.message_handler(state=Daily.daily_set_timezone, content_types=types.ContentType.TEXT)
async def process_daily_set_timezone(msg: Message):
    if number_in_range(msg.text, -1, 24):
        # sql.set_timezone(msg.from_user.id, msg.text)
        sql_pg.set_timezone(msg.from_user.id, msg.text)
        await msg.answer(Daily_message.your_first_task.value)
        await Daily.add_first_tasks.set()
    else:
        await msg.answer(General_message.set_timezone.value)
        return


@dp.message_handler(state=Daily.add_first_tasks, content_types=types.ContentType.TEXT)
async def process_add_first_tasks(msg: Message, state: FSMContext):
    """
    Первоначальное добавление задач, сразу после регистрации
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Отмена')
    await msg.answer(text='Список дел: ', reply_markup=keyboard)
    if msg.text.lower() == 'отмена':
        await state.finish()
        await msg.answer(text='Вы всегда можете просмотреть списак вывав команду /daily. Чтобы завершить задание '
                              'просто нажмите на него',
                         reply_markup=ReplyKeyboardRemove())
    else:
        # sql.add_new_task(msg.from_user.id, msg.text, int(time.time()))
        sql_pg.add_new_task(msg.from_user.id, msg.text, int(time.time()))
        tasks_list = ''
        sequential_number = 1
        # for task in sql.get_tasks_list(msg.from_user.id):
        for task in sql_pg.get_tasks_list(msg.from_user.id):
            tasks_list += str(sequential_number) + '.  ' + str(task[1]) + '\n'
            sequential_number += 1
        await msg.answer(tasks_list)


# ##############################################################
# Функции для новых пользователей
# Добавляют пользователя в БД проводят первоночальную настройку
# ##############################################################
@dp.callback_query_handler(text_contains='tasks_list')
async def process_show_tasks_list(call: CallbackQuery):
    # Если в названии callback есть идентификатор задания
    # Мы ищем его среди незавершенных задач и присваиваем этой задаче статус 1 (Завершена)
    # for task in sql.get_tasks_list(call.from_user.id):
    for task in sql_pg.get_tasks_list(call.from_user.id):
        if str(task[0]) in call.data:
            # sql.task_complete(task[0])
            sql_pg.task_complete(task[0])
            await call.message.answer(text=f'Задание "{task[1]}" завершено')

    inline_daily_function = InlineKeyboardMarkup()

    # for task in sql.get_tasks_list(call.from_user.id):
    for task in sql_pg.get_tasks_list(call.from_user.id):
        # При нажатии на кнопку к названию callback добавляется идентификатор задания
        inline_daily_function.add(InlineKeyboardButton(text=f'{task[1]}', callback_data=f'tasks_list:{task[0]}'))
    inline_daily_function.add(InlineKeyboardButton(text=f'{General_message.cancel.value}',
                                                   callback_data='cancel_daily'))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text='Список задач', reply_markup=inline_daily_function)


@dp.callback_query_handler(text_contains='add_new_task')
async def process_add_new_task_state_set(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await Daily.add_new_task.set()
    await call.message.answer('<b><i>---[ Напишите новое задание ]--</i></b>',
                              parse_mode='HTML')


@dp.message_handler(state=Daily.add_new_task, content_types=types.ContentType.TEXT)
async def process_add_new_task(msg: Message, state: FSMContext):
    # sql.add_new_task(msg.from_user.id, msg.text, int(time.time()))
    sql_pg.add_new_task(msg.from_user.id, msg.text, int(time.time()))
    await state.finish()
    await msg.answer(text='Список задач', reply_markup=inline_daily_function_btn)


@dp.callback_query_handler(text_contains='daily_options')
async def process_daily_options(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=f'{General_message.title_menu_options.value}',
                              reply_markup=inline_daily_options_btn,
                              parse_mode='HTML')


@dp.callback_query_handler(text_contains='options_start_time')
async def process_options_start_time(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=Daily_message.start_time.value)
    await Daily.daily_options_start_time.set()


@dp.message_handler(state=Daily.daily_options_start_time, content_types=types.ContentType.TEXT)
async def process_options_set_start_time(msg: Message, state: FSMContext):
    # if number_in_range(msg.text, -1, 24):
    if validation_time(msg.text):
        # sql.option_set_start_time(msg.from_user.id, normalize_time_to_pattern(msg.text))
        sql_pg.option_set_start_time(msg.from_user.id, normalize_time_to_pattern(msg.text))
        update_mailing_daily_list(msg.from_user.id)
        await state.finish()
        await msg.answer(text=f'{General_message.title_menu_options.value}',
                         reply_markup=inline_daily_options_btn,
                         parse_mode='HTML')
    else:
        await msg.answer(text=Daily_message.start_time.value)
        return


@dp.callback_query_handler(text_contains='options_finish_time')
async def process_options_finish_time(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=Daily_message.finish_time.value)
    await Daily.daily_options_finish_time.set()


@dp.message_handler(state=Daily.daily_options_finish_time, content_types=types.ContentType.TEXT)
async def process_options_set_finish_time(msg: Message, state: FSMContext):
    if validation_time(msg.text):
        # sql.option_set_finish_time(msg.from_user.id, normalize_time_to_pattern(msg.text))
        sql_pg.option_set_finish_time(msg.from_user.id, normalize_time_to_pattern(msg.text))
        update_mailing_daily_list(msg.from_user.id)
        await state.finish()
        await msg.answer(text=f'{General_message.title_menu_options.value}',
                         reply_markup=inline_daily_options_btn,
                         parse_mode='HTML')
    else:
        await msg.answer(text=Daily_message.finish_time.value)
        return


@dp.callback_query_handler(text_contains='options_how_many_time')
async def process_options_how_many_time(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=Daily_message.how_many_time.value)
    await Daily.daily_options_how_many_time.set()


@dp.message_handler(state=Daily.daily_options_how_many_time, content_types=types.ContentType.TEXT)
async def process_options_set_how_many_time(msg: Message, state: FSMContext):
    if number_in_range(msg.text, -1, 24):
        # sql.option_set_how_many_time(msg.from_user.id, msg.text)
        sql_pg.option_set_how_many_time(msg.from_user.id, msg.text)
        update_mailing_daily_list(msg.from_user.id)
        await state.finish()
        await msg.answer(text=f'{General_message.title_menu_options.value}',
                         reply_markup=inline_daily_options_btn,
                         parse_mode='HTML')
    else:
        await msg.answer(text=Daily_message.how_many_time.value)
        return


# Если в одной из секций нажата кнопка Отмена, возвращаем пользователя в меню daily
@dp.callback_query_handler(text_contains='cancel_daily')
async def process_cancel_daily(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=f'{General_message.choice_action.value}', reply_markup=inline_daily_function_btn)


# Для выхода из секции Daily. Пользователю предлагается ввести команду для просмотра доступных подписок
@dp.callback_query_handler(text_contains='quit_daily')
async def process_quit_daily(call: CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(General_message.show_list_subscribe.value)


# TODO Продумать куда вынести такие сервисные функции
def update_mailing_daily_list(user_id):
    # sql.remove_mailing_list(user_id, 1)
    sql_pg.remove_mailing_list(user_id, 1)
    # options = sql.get_options_daily(user_id)
    options = sql_pg.get_options_daily(user_id)
    dispatch_time = calculate_dispatch_time(options[0], options[1], options[2])
    # sql.set_mailing_daily_list(user_id, dispatch_time)
    sql_pg.set_mailing_daily_list(user_id, dispatch_time)
