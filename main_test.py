from extractor import Extract_data
#from src.solver import SolveurPPC
from src import date_converter
from datetime import datetime, timedelta
import pandas as pd
from src import Solution
import numpy as np


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

sol = "./Solution_PPC_60_sec_0_type_Restart_k_1.json"

# #test tache ouest - plus tard
# #apply_and_check_nouvelle_livraison(2, 4, 2019, "W10111C", sol)

# #test taux occupation
Solution.taux_occupation_operateurs(sol)
