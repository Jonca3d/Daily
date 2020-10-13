import re


# Вернуть True, если переменная является числом из заданного диапазона
def number_in_range(var, minimum, maximum):
    if var.isdigit():
        if minimum < int(var) < maximum:
            return True
        else:
            return False
    else:
        return False


def validation_time(time):
    pattern = r'\d\d'
    if len(time.split(':')) == 2:
        time = normalize_time_to_pattern(time).split(':')
        if (re.fullmatch(pattern, time[0])) and (re.fullmatch(pattern, time[1])):
            if (-1 < int(time[0]) < 24) and (-1 < int(time[1]) < 60):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def normalize_time_to_pattern(time):
    time = time.split(':')
    if len(str(time[0])) < 2:
        time[0] = '0' + str(time[0])

    if len(str(time[1])) < 2:
        time[1] = '0' + str(time[1])

    return str(time[0]) + ':' + str(time[1])
