from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.users.message_answer import General as GeneralM

# Кнопки которые выводятся при вызове команды /daily, если пользователь уже подписан
inline_daily_function_btn = InlineKeyboardMarkup()

inline_show_tasks_list = InlineKeyboardButton('Просмотреть список заданий', callback_data='show_tasks_list')
inline_add_new_task = InlineKeyboardButton('Добавить новое задание', callback_data='add_new_task')
inline_daily_options = InlineKeyboardButton('Настройки оповещений', callback_data='daily_options')
inline_cancel = InlineKeyboardButton('Отмена', callback_data='quit_daily')

inline_daily_function_btn.add(inline_show_tasks_list)
inline_daily_function_btn.add(inline_add_new_task)
inline_daily_function_btn.add(inline_daily_options)
inline_daily_function_btn.add(inline_cancel)


# Опции Daily
inline_daily_options_btn = InlineKeyboardMarkup()

inline_daily_options_btn.add(InlineKeyboardButton(text='Задать время начала',
                                                  callback_data='options_start_time'))
inline_daily_options_btn.add(InlineKeyboardButton(text='Задать время окончания',
                                                  callback_data='options_finish_time'))
inline_daily_options_btn.add(InlineKeyboardButton(text='Задать колличество напоминаний',
                                                  callback_data='options_how_many_time'))
inline_daily_options_btn.add(InlineKeyboardButton(text=f'{GeneralM.cancel.value}',
                                                  callback_data='cancel_daily'))
