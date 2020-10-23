import psycopg2

import db.config as db

conn = psycopg2.connect(dbname=db.DATABASE,
                        user=db.USERNAME,
                        password=db.PASSWORD,
                        host=db.HOST)


def init_db_tables():
    """
    При старте бота вызывается эта функция и проверяются на существование необходимые таблицы.
    В случае если таблица отсутствует функция создает таблицы.
    Назначение функции проинициализировать БД при первом старте бота.
    :return:
    """
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS users('
                   'telegram_id INTEGER PRIMARY KEY, '
                   'first_name VARCHAR(40), '
                   'last_name VARCHAR(40), '
                   'timezone INTEGER'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS subscriptions('
                   'id INTEGER PRIMARY KEY, '
                   'name VARCHAR(40), '
                   'description TEXT'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS user_subs('
                   'user_id INTEGER NOT NULL, '
                   'subscription_id INTEGER NOT NULL, '
                   'status INTEGER, '
                   'FOREIGN KEY("user_id") REFERENCES "users"("telegram_id"),'
                   'FOREIGN KEY("subscription_id") REFERENCES "subscriptions"("id")'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS options_daily('
                   'user_id INTEGER PRIMARY KEY, '
                   'start_time VARCHAR(20),'
                   'finish_time VARCHAR(20), '
                   'how_many_time INTEGER NOT NULL'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS mailer_list('
                   'id SERIAL PRIMARY KEY, '
                   'time_id VARCHAR(10) NOT NULL, '
                   'user_id INTEGER NOT NULL, '
                   'subscription_id INTEGER NOT NULL'
                   ');')
    conn.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS daily_tasks('
                   'id SERIAL PRIMARY KEY, '
                   'user_id INTEGER NOT NULL, '
                   'description VARCHAR(200) NOT NULL, '
                   'time_stamp INTEGER NOT NULL, '
                   'status INTEGER NOT NULL, '
                   'FOREIGN KEY("user_id") REFERENCES "users"("telegram_id")'
                   ');')
    conn.commit()


def init_db_data():
    cursor = conn.cursor()
    cursor.execute('SELECT EXISTS(SELECT * FROM subscriptions WHERE id = 1)')
    result = cursor.fetchone()
    if not result[0]:
        cursor.execute('INSERT INTO subscriptions(id, name, description) '
                       'VALUES(%s, %s, %s);',
                       (1, "daily", "Каждый день отправляет запрос пользователю на список дел заданное "
                                    "колличесво раз за день напоминает о незавершенных делах"))
        conn.commit()
