import sys
sys.path.append("..")
from src.date_converter import *


# Test end_date_calc
start = datetime.datetime.strptime("2010-12-10 8:55:0", "%Y-%m-%d %H:%M:%S")
duration = datetime.timedelta(hours= 3)
end = datetime.datetime.strptime("2010-12-10 11:55:0", "%Y-%m-%d %H:%M:%S")
assert (end_date_calc(start, duration) == end)

start = datetime.datetime.strptime("2010-12-10 12:55:0", "%Y-%m-%d %H:%M:%S")
duration = datetime.timedelta(hours= 3)
end = datetime.datetime.strptime("2010-12-10 16:55:0", "%Y-%m-%d %H:%M:%S")
assert (end_date_calc(start, duration) == end)

start = datetime.datetime.strptime("2020-12-27 12:55:0", "%Y-%m-%d %H:%M:%S")
duration = datetime.timedelta(hours= 10)
end = datetime.datetime.strptime("2020-12-28 18:00:0", "%Y-%m-%d %H:%M:%S")
assert (end_date_calc(start, duration) == end)

start = datetime.datetime.strptime("2021-01-01 00:00:0", "%Y-%m-%d %H:%M:%S")
duration = datetime.timedelta(hours= 8.5)
end = datetime.datetime.strptime("2021-01-04 16:30:0", "%Y-%m-%d %H:%M:%S")
assert (end_date_calc(start, duration) == end)