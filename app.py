import asyncio


from handlers.users.daily import send_time

if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp
    # TODO Добавить вызов функции которая проинициализирует БД, если она не существует
    loop = asyncio.get_event_loop()
    loop.create_task(send_time(10))
    # TODO добавить асинхронную функцию которая будет брать подготовленные данные и отправлять пользователям
    executor.start_polling(dp, loop=loop)
