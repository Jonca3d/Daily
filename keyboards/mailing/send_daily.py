from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.db_sqlite_api.sqlite import sql_exec as sql
from handlers.users.message_answer import General


def send(user_id):
    inline_daily_function = InlineKeyboardMarkup()
    for task in sql.get_tasks_list(user_id):
        # При нажатии на кнопку к названию callback добавляется идентификатор задания
        inline_daily_function.add(InlineKeyboardButton(text=f'{task[1]}',
                                                       callback_data=f'tasks_list:{task[0]}'))
    inline_daily_function.add(InlineKeyboardButton(text=f'{General.cancel.value}',
                                                   callback_data='cancel_daily'))
