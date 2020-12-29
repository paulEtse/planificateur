import datetime
import holidays

startdate = datetime.datetime(2019,11,1)

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


def convert_to_work_time(ts):
    #print(ts, datetime.datetime.timestamp(startdate))
    if ts <= datetime.datetime.timestamp(startdate) :
        #print("return 0")
        return(0)
    else:
        goal_date = datetime.datetime.fromtimestamp(ts)
        cur_date = startdate
        time_to_return = 0
        while(cur_date <= goal_date):
            #print(cur_date)
            if(cur_date.isoweekday() > 5 or cur_date in holidays.FR()):
                cur_date += datetime.timedelta(days = 1)
            else:
                time_to_return += 2*7*6
                cur_date += datetime.timedelta(days = 1)
        return(time_to_return)



def convert_to_timestamp(worktime):
    if worktime == 0:
        return(startdate)
    else:
        date_to_return = startdate
        copy = worktime
        while(copy > 2*7*6):
            if(date_to_return.isoweekday() > 5 or date_to_return in holidays.FR()):
                date_to_return += datetime.timedelta(days = 1)
            else:
                copy -= 2*7*6
                date_to_return += datetime.timedelta(days = 1)
        date_to_return += datetime.timedelta(seconds=worktime*60*10)
        return(datetime.datetime.timestamp(date_to_return))





