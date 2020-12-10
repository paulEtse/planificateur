import datetime
import holidays

def end_date_calc(start_date, duration):
    fr_holidays = fr_holidays = holidays.FR()
    end_date = start_date
    #print(str(duration))
    while duration.total_seconds() > 0:
        # weekend
        max_day = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=14, minute=0)
        if (end_date.isoweekday() > 5 or end_date in fr_holidays):
            end_date = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=0, minute=0)+datetime.timedelta(days = 1)
        elif max_day - end_date > duration:
            end_date = end_date + duration
            duration = datetime.timedelta(0)
        else:
            duration = duration - (max_day - end_date)
            end_date = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=0, minute=0)+datetime.timedelta(days = 1)
    return end_date
