from extractor import Extract_data
#from src.solver import SolveurPPC
from src import date_converter
from datetime import datetime, timedelta
import pandas as pd
from src import Solution
import numpy as np

from dateutil import parser
from datetime import datetime
import requests
import os
import time

from src.hidden_prints import HiddenPrints
from src import Solution
from src.solver.SolveurPPC import SolveurPPC

from docplex.cp.config import context


# date = datetime(2019,11,4,1,20,0)

# for i in range(50):
#     ts = datetime.timestamp(date)
#     print("Original date : ", date, ts)
#     worktime = date_converter.convert_to_work_time(ts)
#     print("worktime :" , worktime)
#     converted = date_converter.convert_to_timestamp(worktime)
#     print("converted date : ", datetime.fromtimestamp(converted) ,converted )
#     date = date + timedelta(seconds = 60*60)


# for i in range(0,1000):
#     wt = i*6
#     date = date_converter.convert_to_timestamp(wt)
#     wt_bis = date_converter.convert_to_work_time(date)
#     # if (not wt == wt_bis):
#     print("Original wt : ", wt)
#     print("date :" , date, datetime.fromtimestamp(date) )
#     print("convcerted worktime :" , wt_bis)
#     print(wt == wt_bis)


# from extractor import Extract_data
# from src.solver.SolveurPPC import SolveurPPC


# ppc = SolveurPPC()
# ppc.create_model(0,10, "Restart", 1)

#-------------------------------------------------------------------------------------------

r = requests.get("https://qrfx7lea3b.execute-api.eu-west-3.amazonaws.com/dev/project/solution?gantt=0")
#sol_df = Solution
# # #test tache ouest - plus tard
# # #apply_and_check_nouvelle_livraison(2, 4, 2019, "W10111C", sol)

#test taux occupation
Solution.taux_occupation_operateurs_by_weeks(r.json(),1)


# livraisons = pd.read_excel("./data/livraison guides.xlsx",parse_dates=['livraison au MAG AIT'])
# livraisons.to_json(path_or_buf ="./data/livraison guides.json",date_unit='s')

# livraison2 = pd.read_json(path_or_buf="./data/livraison guides.json",convert_dates=['livraison au MAG AIT'])

# print(livraisons)
# print(livraison2)
