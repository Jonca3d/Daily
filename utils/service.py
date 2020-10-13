

def convert_time_to_minutes(time):
    """
    Функция на вход получает массив из двух элементов
    Где [0] - часы [1] - минуты
    :param time:
    :return: Возвращается текущее время в минутах прошедших с полуночи
    """
    time = time.split(':')
    return int(time[0]) * 60 + int(time[1])


def convert_minutes_to_time(minutes):
    """
    Функция получает на вход колличество минут
    :param minutes:
    :return: Возвращает строку в форммате hh:mm где hh - часы, mm - минуты
    """
    hours = int(minutes) // 60
    minute = int(minutes) - int(hours) * 60

    if len(str(hours)) != 2:
        hours = '0' + str(hours)

    if len(str(minute)) != 2:
        minute = '0' + str(minute)

    return str(hours) + ':' + str(minute)
