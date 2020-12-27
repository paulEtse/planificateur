import datetime
import holidays

fr_holidays = holidays.FR()


def isHolliday(date):
    return date.isoweekday() > 5 or date in fr_holidays


def start1_of_date(date):
    return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=7, minute=0)


def start2_of_date(date):
    return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=15, minute=0)


def end1_of_date(date):
    return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=14, minute=0)


def end2_of_date(date):
    return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=22, minute=0)


def next_start(date):
    if isHolliday(date):
        return next_start(start1_of_date(date) + datetime.timedelta(days=1))
    elif date <= start1_of_date(date):
        return start1_of_date(date)
    elif date <= start2_of_date(date):
        return start2_of_date(date)
    else:
        return next_start(start1_of_date(date) + datetime.timedelta(days=1))


def next_end(date):
    if isHolliday(date):
        return next_end(end1_of_date(date) + datetime.timedelta(days=1))
    if date < end1_of_date(date):
        return end1_of_date(date)
    if date < end2_of_date(date):
        return end2_of_date(date)
    else:
        return next_end(end1_of_date(date + datetime.timedelta(days=1)))


def end_date_calc(start_date, duration):
    end_date = start_date
    if duration.total_seconds() < 0:
        raise Exception
    if duration.total_seconds() == 0:
        return end_date
    else:
        if isHolliday(end_date):
            return end_date_calc(next_start(end_date), duration)
        end = next_end(end_date)
        if end - end_date > duration:
            return end_date + duration
        else:
            delta = (end - end_date)
            d = duration - delta
            s = next_start(end)
            return end_date_calc(s, d)