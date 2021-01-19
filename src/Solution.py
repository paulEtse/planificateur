import pandas as pd
from src import date_converter
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio
import json

def create_solution_from_PPC_result(ppc_solution):
    sol = pd.DataFrame(columns = ["Task", "Start","Finish", "Part","IsPresent"] )
    print(sol)
    #interval.sort(key = self.get_start)

    i=0
    for interval in ppc_solution:
        name = interval.get_name()
        #print(name)
        if not "op" in name :
            if interval.is_present() : 
                start = date_converter.convert_to_timestamp(interval.get_start())
                end = date_converter.convert_to_timestamp(interval.get_end())
                sol.loc[i] = [name[-6:], start, end, name[:-6], True ]
            else:
                 sol.loc[i] = [name[-6:],None, None, name[:-6], False]
        else :
            sol.loc[i] = [name[-6:],None, None, name[:-6], False]
        i+=1
    return(sol)
        


def generate_Solution_from_json(json):
    solution = pd.read_json(path_or_buf=json)
    return(solution)

def generate_json_from_Solution(solution, name):
    solution.to_json(path_or_buf ="./" + name + ".json")


def create_html_gantt_from_solution(solution, name): 
    print(solution)
    solution = solution[solution.IsPresent == True]
    fig = ff.create_gantt(solution,index_col='Part',show_colorbar=True, group_tasks=True)
    fig.write_html("./" + name + ".html")