# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 09:35:11 2020

@author: Arnaud
"""
from src.solver import SolveurPPC 
from extractor import Extract_data

timeOUEST, req_matOUEST, req_taskOUEST = Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
print(req_matOUEST)