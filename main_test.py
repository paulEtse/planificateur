from extractor import Extract_data
from src.solver import SolverPLNE
from src import date_converter
from datetime import datetime, timedelta

date = datetime(2019,11,1,1,0,0)


for i in range(50):
    ts = datetime.timestamp(date)
    print("Original date : ", date, ts)
    worktime = date_converter.convert_to_work_time(ts)
    print("worktime :" , worktime)
    converted = date_converter.convert_to_timestamp(worktime)
    print("converted date : ", datetime.fromtimestamp(converted) ,converted )
    date = date + timedelta(days = 1)





