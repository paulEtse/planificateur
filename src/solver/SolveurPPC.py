# -*- coding: utf-8 -*-

#import SolverInterface
from docplex.cp.model import CpoModel
from extractor import Extract_data
from src import Solution
import sys

class SolveurPPC():
    def solve_from_skratch():
        print("")
        
    
        
    def create_model():
        mdl = CpoModel(name = "TAS Scheduling")
        
    def extract_datas():
        Extract_data.extract_tasks_from_excel()
        
        
        
# =============================================================================
# if name == "__main__":
#     #sys.path.append('./src')
#     ppc = SolveurPPC()
#     print(ppc.extract_datas())
#         
# =============================================================================
        