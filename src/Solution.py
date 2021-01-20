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
    solution = pd.read_json(json, orient="split")
    return(solution)

def generate_json_from_Solution(solution):
    return solution.to_json(orient="split")


def create_html_gantt_from_solution(solution, name): 
    #print(solution)
    solution = solution[solution.IsPresent == True]
    solution["Start"] = solution["Start"].apply(lambda a : a*1000)
    solution["Finish"] = solution["Finish"].apply(lambda a :a*1000)
    fig = ff.create_gantt(solution,index_col='Part',show_colorbar=True, group_tasks=True)
    fig.write_html("./" + name + ".html")


def taux_occupation_operateurs(sol):
    df = generate_Solution_from_json(sol)
    
    return taux_occupation_operateurs_dataframe(df)

def taux_occupation_operateurs_by_weeks(sol, nb_weeks):
    df = generate_Solution_from_json(sol)

    all_proportions = []

    #calcul nb portions
    timestamp_min = df["Start"].min()
    timestamp_max = df["Finish"].max()-1

    min_datetime = datetime.datetime.fromtimestamp(date_min)
    max_datetime = datetime.datetime.fromtimestamp(date_max)

    i = 0
    current_datetime = min_datetime
    while(current_datetime < max_datetime):
        #calcul des dates de début, de fin, et de prochain début
        end_period_datetime = current_datetime + datetime.timedelta(days=(7*nb_weeks -1))
        next_period_datetime = end_period_datetime + datetime.timedelta(days=1)
        last_datetime = min(max_datetime, end_period_datetime)

        current_timestamp = datetime.datetime.timestamp(current_datetime)
        next_timestamp = datetime.datetime.timestamp(next_period_datetime)

        all_proportions.append([current_datetime, last_datetime])
        
        #filtre sur le dataframe
        current_df = df[df.Start < next_timestamp and df.Finish >= current_timestamp]

        #calcul du taux d'occupation et ajout au résultat final
        period_result = taux_occupation_operateurs_dataframe(current_df, current_timestamp, next_timestamp)
        all_proportions[i].append(period_result)

        #incrémentation
        i = i + 1
        current_datetime = next_period_datetime
    
    #all_proportions = une liste de [first_day, last_day (inclu), taux_occupation_result]
    return all_proportions


def taux_occupation_operateurs_dataframe(sol_df, start_point = None, next_start_point = None):
    df2 = sol_df[sol_df.IsPresent == True]

    df2["Start"] = df2["Start"].apply(lambda a : date_converter.convert_to_work_time(a))
    df2["Finish"] = df2["Finish"].apply(lambda a : date_converter.convert_to_work_time(a))

    time_min = df2["Start"].min()
    time_max = df2["Finish"].max()-1

    time_start_point = date_converter.convert_to_work_time(start_point)
    time_next_start_point = date_converter.convert_to_work_time(next_start_point)

    if(start_point != None and next_start_point != None):
        time_min = max(time_min, time_start_point)
        time_max = min(time_max, time_next_start_point-1)

    #initialisation dataframe occupation
    list_occupations = []

    for index_time in range(time_max - time_min + 1):
        #(nb meca working, nb qc working)
        list_occupations.append([0, 0])

    #modification list_occupations
    for task in df2.itertuples():
        first_time = max(task.Start, time_min) - time_min
        last_time = min(task.Finish, time_max) - 1 - time_min

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
    total_len = len(time_max - time_min + 1)
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
