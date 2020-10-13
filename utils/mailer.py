from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import bot
from utils.db_sqlite_api.sqlite import sql_exec as sql
from keyboards.inline.daily_buttons import GeneralM
from utils.service import convert_time_to_minutes, convert_minutes_to_time


async def send_daily_lists():
    now = datetime.now().strftime('%H:%M')
    daily_users_list = sql.get_mailing_list(now, 1)
    if len(daily_users_list) > 0:
        inline_daily_function = InlineKeyboardMarkup()
        for user in daily_users_list[0]:
            for task in sql.get_tasks_list(user):
                inline_daily_function.add(InlineKeyboardButton(text=f'{task[1]}',
                                                               callback_data=f'tasks_list:{task[0]}'))
            inline_daily_function.add(InlineKeyboardButton(text=f'{GeneralM.cancel.value}',
                                                           callback_data='cancel_daily'))
            await bot.send_message(chat_id=user, text='Список задач', reply_markup=inline_daily_function)


def calculate_dispatch_time(start_time, finish_time, count):
    """
    Функция возвращает список со временем рассылки
    :param start_time:
    :param finish_time:
    :param count:
    :return:
    """
    mailing_time_list = [start_time, finish_time]

    start_time = convert_time_to_minutes(start_time)
    finish_time = convert_time_to_minutes(finish_time)

    if finish_time > start_time:
        difference_of_values = finish_time - start_time
    elif start_time > finish_time:
        difference_of_values = 1440 - (start_time - finish_time)
    else:
        difference_of_values = 1440

    step_to_next_notification = difference_of_values / (int(count) + 1)
    time_next_notification = start_time

    for step in range(int(count)):
        time_next_notification = time_next_notification + step_to_next_notification
        if time_next_notification > 1440:
            time_next_notification = time_next_notification - 1440
        mailing_time_list.append(convert_minutes_to_time(time_next_notification))

    return mailing_time_list
