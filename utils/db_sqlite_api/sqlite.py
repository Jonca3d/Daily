import sqlite3
# TODO Изменить способ запроса в БД
#     """
#     Вынести сами запросы в отдельные переменные
#     В команде execute подставлять необходимые значени
#     """


def create_connection(path):
    conn = sqlite3.connect(path)
    return conn


connection = create_connection('data/database/db.sqlite')


class sql_exec:

    #########################################################################
    #
    # Запросы на проверку сеществования записи
    #
    #########################################################################
    @staticmethod
    def check_user_exists(user_id):
        cursor = connection.cursor()
        cursor.execute(f'''
                        SELECT EXISTS(SELECT * FROM users WHERE telegram_id = {user_id})
                        ''')
        result = cursor.fetchone()
        return result

    @staticmethod
    def check_user_subscribe_to_daily(user_id):
        cursor = connection.cursor()
        cursor.execute(f'''
                        SELECT EXISTS(SELECT * FROM user_subs WHERE (user_id = {user_id} AND subscription_id = 1))
                        ''')
        return cursor.fetchone()

    @staticmethod
    def check_timezone_options(user_id):
        cursor = connection.cursor()
        cursor.execute(f'SELECT timezone FROM users WHERE telegram_id = {user_id}')
        return cursor.fetchone()

    @staticmethod
    def add_new_user(user_id, first_name, last_name):
        cursor = connection.cursor()
        cursor.execute('''
                        INSERT INTO users (telegram_id, first_name, last_name)
                        VALUES("{}", "{}", "{}")
                        '''.format(user_id, first_name, last_name))
        connection.commit()

    @staticmethod
    def subscription_to_daily(user_id, start_time, finish_time, how_many_time, status):
        cursor = connection.cursor()
        cursor.execute('''
                        INSERT INTO user_subs (user_id, subscription_id, status)
                        VALUES("{}", 1, "{}")
                        '''.format(user_id, status))
        connection.commit()

        cursor.execute('''
                        INSERT INTO options_daily (user_id, start_time, finish_time, how_many_time)
                        VALUES("{}", "{}", "{}", "{}")
                        '''.format(user_id, start_time, finish_time, how_many_time))
        connection.commit()

    @staticmethod
    def add_new_task(user_id, description, time_stamp):
        cursor = connection.cursor()
        cursor.execute('''
                        INSERT INTO daily_tasks (user_id, description, time_stamp, status)
                        VALUES("{}", "{}", "{}", 0)
                        '''.format(user_id, description, time_stamp))
        connection.commit()

    @staticmethod
    def get_tasks_list(user_id):
        cursor = connection.cursor()
        cursor.execute('SELECT id, description FROM daily_tasks WHERE (status = 0 AND user_id={})'.format(user_id))
        return cursor.fetchall()

    @staticmethod
    def task_complete(task_id):
        cursor = connection.cursor()
        cursor.execute('''
                        UPDATE daily_tasks SET status = 1 WHERE id = {}
                        '''.format(task_id))
        connection.commit()

    @staticmethod
    def option_set_start_time(user_id, start_time):
        """
        Поменять время первого оповещения пользователя
        :param user_id: Идентификатор пользователя
        :param start_time: Время в которое бот будет напоминать о том что надо написать чек лист на день
        :return:
        """
        cursor = connection.cursor()
        data = (start_time, user_id)
        cursor.execute('UPDATE options_daily SET start_time = ? WHERE user_id = ?', data)
        connection.commit()

    @staticmethod
    def option_set_finish_time(user_id, finish_time):
        """
        Поменять время последнего оповещения пользователя за день
        :param user_id: Идентификатор пользователя
        :param finish_time: Время в которое бот будет напоминать о том что надо проверить чек лист за день
        :return:
        """
        cursor = connection.cursor()
        data = (finish_time, user_id)
        cursor.execute('UPDATE options_daily SET finish_time = ? WHERE user_id = ?', data)
        connection.commit()

    @staticmethod
    def option_set_how_many_time(user_id, how_many_time):
        """
        Поменять колмчество раз, которое бот будет присылать оповещения от этой секции бота
        :param user_id: Идентификатор пользователя
        :param how_many_time: Колличество оповещений за период от первого до последнего, не включая их
        :return:
        """
        cursor = connection.cursor()
        cursor.execute('''
                            UPDATE options_daily SET how_many_time = {} WHERE user_id = {}
                            '''.format(how_many_time, user_id))
        connection.commit()

    @staticmethod
    def set_timezone(user_id, timezone):
        cursor = connection.cursor()
        cursor.execute(f'UPDATE users SET timezone = {timezone} WHERE telegram_id = {user_id}')
        connection.commit()

    @staticmethod
    def get_all_users():
        cursor = connection.cursor()
        cursor.execute('SELECT telegram_id FROM users')
        return cursor.fetchall()

    @staticmethod
    def set_mailing_daily_list(user_id, time_list):
        cursor = connection.cursor()
        for num in range(len(time_list)):
            data = [time_list[num], user_id, 1]
            cursor.execute('INSERT INTO mailer_list (time_id, user_id, subscription_id) VALUES(?, ?, ?)', data)
            connection.commit()

    @staticmethod
    def remove_mailing_list(user_id, subscription_id):
        cursor = connection.cursor()
        data = [user_id, subscription_id]
        cursor.execute('DELETE FROM mailer_list WHERE (user_id = ? AND subscription_id = ?)', data)
        connection.commit()

    @staticmethod
    def get_options_daily(user_id):
        cursor = connection.cursor()
        cursor.execute('SELECT start_time, finish_time, how_many_time '
                       'FROM options_daily '
                       'WHERE user_id = ?', [user_id])
        return cursor.fetchone()

    @staticmethod
    def get_mailing_list(time, subscription):
        cursor = connection.cursor()
        data = [time, subscription]
        cursor.execute('SELECT user_id FROM mailer_list WHERE (time_id = ? AND subscription_id = ?)', data)

        return cursor.fetchall()
