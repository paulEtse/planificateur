import pandas as pd
from src import date_converter
import pandas as pd
from datetime import datetime
import numpy as np
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
    solution["Start"] = solution["Start"].apply(lambda a : a*1000)
    solution["Finish"] = solution["Finish"].apply(lambda a :a*1000)
    fig = ff.create_gantt(solution,index_col='Part',show_colorbar=True, group_tasks=True)
    fig.write_html("./" + name + ".html")


def taux_occupation_operateurs(sol):
    df = generate_Solution_from_json(sol)
            
    df2 = df[df.IsPresent == True]

    df2["Start"] = df2["Start"].apply(lambda a : date_converter.convert_to_work_time(a))
    df2["Finish"] = df2["Finish"].apply(lambda a : date_converter.convert_to_work_time(a))

    #initialisation dataframe occupation
    time_min = df2["Start"].min()
    time_max = df2["Finish"].max()-1

    list_occupations = []

    for index_time in range(time_max - time_min + 1):
        #(nb meca working, nb qc working)
        list_occupations.append([0, 0])

    #modification list_occupations
    for task in df2.itertuples():
        first_time = task.Start - time_min
        last_time = task.Finish - 1 - time_min

        if (task.Part == "kitting " or task.Part == "meca "):
            #print("ok meca or kitting")
            nb_meca_to_add = 1

            #Cas des kitting a plusieurs meca
            if (task.Part == "kitting "):
                #temps passé pour 18 unités de travail de tâche
                time_task = last_time - first_time + 1
                if (time_task == 9):
                    nb_meca_to_add = 2
                elif (time_task == 6):
                    nb_meca_to_add = 3
                else:
                    #deja 1 meca pris en compte
                    #print("temps du kitting : ", time_task)
                    pass

            for t in range(first_time, last_time + 1):
                list_occupations[t][0] = list_occupations[t][0]+nb_meca_to_add

        elif (task.Part == "qc "):
            #print("ok qc")
            for t in range(first_time, last_time + 1):
                list_occupations[t][1] = list_occupations[t][1]+1


    #transfert en dataframe => calculs
    df_final = pd.DataFrame(np.array(list_occupations), index = list(range(time_max - time_min + 1)), columns = ['nb_meca_working', 'nb_qc_working'])

    #calculs des pourcentages
    total_len = len(df_final.index)
    pourc_meca = []
    pourc_qc = []

    for val in df_final["nb_meca_working"].unique():
        val_df = df_final[df_final.nb_meca_working == val]
        nb_val = len(val_df.index)
        p_val = 100*nb_val/total_len
        pourc_meca.append([val, p_val])

    for val in df_final["nb_qc_working"].unique():
        val_df = df_final[df_final.nb_qc_working == val]
        nb_val = len(val_df.index)
        p_val = 100*nb_val/total_len
        pourc_qc.append([val, p_val])

    df_meca = pd.DataFrame(np.array(pourc_meca), columns = ['nb_meca_working', 'pourcentage']).sort_values(by = 'nb_meca_working')
    df_qc = pd.DataFrame(np.array(pourc_qc), columns = ['nb_qc_working', 'pourcentage']).sort_values(by = 'nb_qc_working')

    print("proportions des opérateurs méca: \n" , df_meca)
    print("proportions des opérateurs qc: \n" , df_qc)

    #print("time_min : ", time_min)
    #print("time_max : ", time_max)

    return df_meca, df_qc
