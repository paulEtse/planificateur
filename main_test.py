from extractor import Extract_data
from src.solver import SolveurPPC
#from src import date_converter
from datetime import datetime, timedelta
import pandas as pd
from src import Solution


#date = datetime(2019,11,1,1,0,0)

#for i in range(50):
#    ts = datetime.timestamp(date)
#    print("Original date : ", date, ts)
#    worktime = date_converter.convert_to_work_time(ts)
#    print("worktime :" , worktime)
#    converted = date_converter.convert_to_timestamp(worktime)
#    print("converted date : ", datetime.fromtimestamp(converted) ,converted )
#    date = date + timedelta(days = 1)

#-------------------------------------------------------------------------------------------

sol = "./Solution_PPC_15_sec.json"
#test tache ouest - plus tard
apply_and_check_nouvelle_livraison(2, 4, 2019, "W10111C", sol)

