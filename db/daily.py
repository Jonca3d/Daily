import psycopg2

import db.config as db

conn = psycopg2.connect(dbname=db.DATABASE,
                        user=db.USERNAME,
                        password=db.PASSWORD,
                        host=db.HOST)


class sql_daily_exe:
    """
    Запросы к БД для работы с секцией бота Daily
    """
    @staticmethod
    def check_user_exists(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS(SELECT * FROM users WHERE telegram_id = %s);', (user_id,))
        result = cursor.fetchone()
        print(result)
        return result

    @staticmethod
    def check_user_subscribe_to_daily(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT EXISTS(SELECT * FROM user_subs WHERE (user_id = %s AND subscription_id = 1))',
                       (user_id,))
        return cursor.fetchone()

    @staticmethod
    def check_timezone_options(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT timezone FROM users WHERE telegram_id = %s', (user_id,))
        return cursor.fetchone()

    @staticmethod
    def add_new_user(user_id, first_name, last_name):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (telegram_id, first_name, last_name) '
                       'VALUES(%s, %s, %s)', (user_id, first_name, last_name))
        conn.commit()

    @staticmethod
    def subscription_to_daily(user_id, start_time, finish_time, how_many_time, status):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_subs(user_id, subscription_id, status) '
                       'VALUES(%s, 1, %s)', (user_id, status))
        conn.commit()

        cursor.execute('INSERT INTO options_daily (user_id, start_time, finish_time, how_many_time) '
                       'VALUES(%s, %s, %s, %s)', (user_id, start_time, finish_time, how_many_time))
        conn.commit()

    @staticmethod
    def add_new_task(user_id, description, time_stamp):
        cursor = conn.cursor()
        cursor.execute('INSERT INTO daily_tasks (user_id, description, time_stamp, status) '
                       'VALUES(%s, %s, %s, 0)', (user_id, description, time_stamp))
        conn.commit()

    @staticmethod
    def get_tasks_list(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT id, description FROM daily_tasks '
                       'WHERE (status = 0 AND user_id = %s)', (user_id,))
        return cursor.fetchall()

    @staticmethod
    def task_complete(task_id):
        cursor = conn.cursor()
        cursor.execute('UPDATE daily_tasks SET status = 1 WHERE id = %s', (task_id,))
        conn.commit()

    @staticmethod
    def option_set_start_time(user_id, start_time):
        """
        Поменять время первого оповещения пользователя
        :param user_id: Идентификатор пользователя
        :param start_time: Время в которое бот будет напоминать о том что надо написать чек лист на день
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('UPDATE options_daily SET start_time = %s WHERE user_id = %s', (start_time, user_id))
        conn.commit()

    @staticmethod
    def option_set_finish_time(user_id, finish_time):
        """
        Поменять время последнего оповещения пользователя за день
        :param user_id: Идентификатор пользователя
        :param finish_time: Время в которое бот будет напоминать о том что надо проверить чек лист за день
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('UPDATE options_daily SET finish_time = %s WHERE user_id = %s', (finish_time, user_id))
        conn.commit()

    @staticmethod
    def option_set_how_many_time(user_id, how_many_time):
        """
        Поменять колмчество раз, которое бот будет присылать оповещения от этой секции бота
        :param user_id: Идентификатор пользователя
        :param how_many_time: Колличество оповещений за период от первого до последнего, не включая их
        :return:
        """
        cursor = conn.cursor()
        cursor.execute('UPDATE options_daily SET how_many_time = %s WHERE user_id = %s', (how_many_time, user_id))
        conn.commit()

    @staticmethod
    def set_timezone(user_id, timezone):
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET timezone = %s WHERE telegram_id = %s', (timezone, user_id))
        conn.commit()

    @staticmethod
    def get_all_users():
        cursor = conn.cursor()
        cursor.execute('SELECT telegram_id FROM users')
        return cursor.fetchall()

    @staticmethod
    def set_mailing_daily_list(user_id, time_list):
        cursor = conn.cursor()
        for num in range(len(time_list)):
            cursor.execute('INSERT INTO mailer_list (time_id, user_id, subscription_id) '
                           'VALUES(%s, %s, %s)', (time_list[num], user_id, 1))
            conn.commit()

    @staticmethod
    def remove_mailing_list(user_id, subscription_id):
        cursor = conn.cursor()
        cursor.execute('DELETE FROM mailer_list '
                       'WHERE (user_id = %s AND subscription_id = %s)', (user_id, subscription_id))
        conn.commit()

    @staticmethod
    def get_options_daily(user_id):
        cursor = conn.cursor()
        cursor.execute('SELECT start_time, finish_time, how_many_time FROM options_daily '
                       'WHERE user_id = %s', (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_mailing_list(time, subscription):
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM mailer_list '
                       'WHERE (time_id = %s AND subscription_id = $s)', (time, subscription))
        return cursor.fetchall()
