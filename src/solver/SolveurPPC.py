# coding=utf-8
#import SolverInterface
from docplex.cp.modeler import end_before_start
from docplex.cp.model import CpoModel, CpoStepFunction, INTERVAL_MIN, INTERVAL_MAX
from docplex.cp.parameters import CpoParameters
import docplex.cp.utils_visu as visu
import os
from extractor import Extract_data
import random
from src import Solution, date_converter
import sys
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio
import requests
import json
import numpy as np

class SolveurPPC:  
    def __init__(self):
        self.timeOUEST, self.req_matOUEST, self.req_taskOUEST = Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
        self.timeEST, self.req_matEST, self.req_taskEST = Extract_data.extract_tasks_from_excel(Extract_data.pathEST)
        self.start_date = datetime.timestamp(datetime(2019,11,5))

        self.date_all_delivery = datetime.timestamp(datetime(2019,2,2))
        self.max_end_timestamp = date_converter.convert_to_work_time(datetime.timestamp(datetime(2020,3,15)))

        self.kitting_time_max = 3 * 6
        self.kitting_time_mid = int(1.5 * 6)
        self.kitting_time_min = 6
        pio.renderers.default = "vscode"

    def solve_from_skratch(self):
        print("")

    def print_gantt(self, solution):
        pass

    

    def add_constraint(self, solution): #,solution,timeout
        baseUrl = 'https://qrfx7lea3b.execute-api.eu-west-3.amazonaws.com/dev'
        r = requests.get(baseUrl + '/project/constraints')

        mdl = self.create_model()
        mdl,sol = self.start_from_solution(mdl, solution)

        for i in range(len(r.json())): 
            yo = pd.DataFrame.from_dict(r.json()[i], orient = 'index')
            print(yo)
            date_de_prise_en_compte = datetime.strptime(yo.iloc[1,0][:10],"%Y-%m-%d") + timedelta(days=1)
            date_modifiee = datetime.strptime(yo.iloc[2,0], "%Y-%m-%d")
            print(date_modifiee)
            print(date_de_prise_en_compte)
            sol = sol[sol.IsPresent == True]
            if(self.apply_and_check_nouvelle_livraison(date_modifiee.day, date_modifiee.month, date_modifiee.year, yo.iloc[0,0], solution)):
                print(sol)
                for (Task, Start, Finish, Part, Ispresent) in sol.values:
                    if date_converter.convert_to_timestamp(int(Start)) < datetime.timestamp(date_de_prise_en_compte):
                        print(Task, Start, Finish, Part, Ispresent)

                # for var in mdl.get_all_variables():
                #     print(var)

                

            else:
                print(False)
                #return("solution deja ok pas de modif") #TODO
                

    def create_model(self):
        mdl = CpoModel(name = "TAS Scheduling")
        #####################################################
        # Creating interval variables for WEST module
        #####################################################
        i = 0
        MS1_vars = []
        MS4_vars = []
        GTW_vars = []
        WEST_vars = []
        table_occupied_WEST = []

        kits_pulse_for_choice = []
        for i in range(len(self.timeOUEST)):
            min_start_time = int(date_converter.convert_to_work_time(datetime.timestamp(pd.to_datetime(self.req_matOUEST.iloc[i,2]))))

            print(min_start_time, self.req_matOUEST.iloc[i,2])
            meca_length = int(self.timeOUEST.iloc[i, 2] / 10)
            qc_length = int(self.timeOUEST.iloc[i, 3] / 10)

            kit_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), name = "kitting " + self.timeOUEST.index[i])
            kit_interval1mec = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = self.kitting_time_max, name = "kitting 1 op " + self.timeOUEST.index[i], optional = True)
            kit_interval2mec = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = self.kitting_time_mid, name = "kitting 2 op " + self.timeOUEST.index[i], optional = True)
            kit_interval3mec = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = self.kitting_time_min, name = "kitting 3 op " + self.timeOUEST.index[i], optional = True)

            mdl.add(mdl.alternative(interval = kit_interval, array = [kit_interval1mec, kit_interval2mec, kit_interval3mec]))

            kits_pulse_for_choice += [kit_interval1mec, kit_interval2mec, kit_interval3mec]

            meca_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = meca_length, name = "meca " + self.timeOUEST.index[i])
            qc_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = qc_length, name = "qc " + self.timeOUEST.index[i])

            table_slot_occupied_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = (0, 9999999999999), name = "Table occupied " + self.timeOUEST.index[i])
            table_occupied_WEST += [table_slot_occupied_interval]

            mdl.add(mdl.end_before_start(kit_interval, meca_interval))
            mdl.add(mdl.end_before_start(meca_interval, qc_interval))

            mdl.add(mdl.start_at_end(table_slot_occupied_interval, kit_interval))
            mdl.add(mdl.start_at_end(meca_interval, table_slot_occupied_interval))
            
            WEST_vars += [kit_interval]
            WEST_vars += [meca_interval]
            WEST_vars += [qc_interval]

            if i < 19:
                MS1_vars += [kit_interval]
                MS1_vars += [meca_interval]
                MS1_vars += [qc_interval]

            elif i >= 45:
                GTW_vars += [kit_interval]
                GTW_vars += [meca_interval]
                GTW_vars += [qc_interval]
            
            else:
                MS4_vars += [kit_interval]
                MS4_vars += [meca_interval]
                MS4_vars += [qc_interval]


        ######################################################
        # Creating interval variables for EAST module
        ######################################################
        FOV_vars = []
        MS2_vars = []
        MS3_vars = []
        EAST_vars = []
        table_occupied_EAST = []

        for i in range(len(self.timeEST)):
            min_start_time = int(date_converter.convert_to_work_time(datetime.timestamp(pd.to_datetime(self.req_matOUEST.iloc[i,2]))))

            meca_length = int(self.timeOUEST.iloc[i, 2] / 10)
            qc_length = int(self.timeOUEST.iloc[i, 3] / 10)
            
            kit_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), name = "kitting " + self.timeEST.index[i])
            kit_interval1mec = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = self.kitting_time_max, name = "kitting 1 op " + self.timeEST.index[i], optional = True)
            kit_interval2mec = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = self.kitting_time_mid, name = "kitting 2 op " + self.timeEST.index[i], optional = True)
            kit_interval3mec = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = self.kitting_time_min, name = "kitting 3 op " + self.timeEST.index[i], optional = True)

            mdl.add(mdl.alternative(interval = kit_interval, array = [kit_interval1mec, kit_interval2mec, kit_interval3mec]))

            kits_pulse_for_choice += [kit_interval1mec, kit_interval2mec, kit_interval3mec]

            meca_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = meca_length, name = "meca " + self.timeEST.index[i])
            qc_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = qc_length, name = "qc " + self.timeEST.index[i])

            table_slot_occupied_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = (0, 9999999999999), name = "Table occupied " + self.timeEST.index[i])
            table_occupied_EAST += [table_slot_occupied_interval]

            mdl.add(mdl.end_before_start(kit_interval, meca_interval))
            mdl.add(mdl.end_before_start(meca_interval, qc_interval))

            mdl.add(mdl.start_at_end(table_slot_occupied_interval, kit_interval))
            mdl.add(mdl.start_at_end(meca_interval, table_slot_occupied_interval))

            EAST_vars += [kit_interval]
            EAST_vars += [meca_interval]
            EAST_vars += [qc_interval]
            
            if i < 11:
                FOV_vars += [kit_interval]
                FOV_vars += [meca_interval]
                FOV_vars += [qc_interval]

            elif i >= 25:
                MS3_vars += [kit_interval]
                MS3_vars += [meca_interval]
                MS3_vars += [qc_interval]

            else:
                MS2_vars += [kit_interval]
                MS2_vars += [meca_interval]
                MS2_vars += [qc_interval]

        ##################################################
        # Setting requirement relations between interval variables
        ##################################################
        for task in MS1_vars:
            for i in range(len(self.req_taskOUEST)):
                if (self.req_taskOUEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskOUEST.iloc[i, 0])):
                        for other_task in WEST_vars:
                            if self.req_taskOUEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in MS4_vars:
            for i in range(len(self.req_taskOUEST)):
                if (self.req_taskOUEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskOUEST.iloc[i, 0])):
                        for other_task in WEST_vars:
                            if self.req_taskOUEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in GTW_vars:
            for i in range(len(self.req_taskOUEST)):
                if (self.req_taskOUEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskOUEST.iloc[i, 0])):
                        for other_task in WEST_vars:
                            if self.req_taskOUEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in MS2_vars:
            for i in range(len(self.req_taskEST)):
                if (self.req_taskEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskEST.iloc[i, 0])):
                        for other_task in EAST_vars:
                            if self.req_taskEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in MS3_vars:
            for i in range(len(self.req_taskEST)):
                if (self.req_taskEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskEST.iloc[i, 0])):
                        for other_task in EAST_vars:
                            if self.req_taskEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in FOV_vars:
            for i in range(len(self.req_taskEST)):
                if (self.req_taskEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskEST.iloc[i, 0])):
                        for other_task in EAST_vars:
                            if self.req_taskEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                mdl.add(mdl.end_before_start(other_task, task))

        ##############################################
        # Adding resources constraints
        ##############################################

        all_tasks = EAST_vars + WEST_vars

        meca_resources = [mdl.pulse(task, 1) for task in EAST_vars if "meca" in task.name]
        meca_resources += [mdl.pulse(task, 1) for task in WEST_vars if "meca" in task.name]
        meca_resources += [mdl.pulse(task, 1) for task in kits_pulse_for_choice if "kitting 1 op" in task.name]
        meca_resources += [mdl.pulse(task, 2) for task in kits_pulse_for_choice if "kitting 2 op" in task.name]
        meca_resources += [mdl.pulse(task, 3) for task in kits_pulse_for_choice if "kitting 3 op" in task.name]

        qc_resources = [mdl.pulse(task, 1) for task in EAST_vars if "qc" in task.name]
        qc_resources += [mdl.pulse(task, 1) for task in WEST_vars if "qc" in task.name]

        work_slots_EAST = [mdl.pulse(task, 1) for task in EAST_vars if "qc" in task.name or "meca" in task.name]
        work_slots_WEST = [mdl.pulse(task, 1) for task in WEST_vars if "qc" in task.name or "meca" in task.name]

        kitting_slots_EAST = [mdl.pulse(task, 1) for task in table_occupied_EAST]
        kitting_slots_EAST += [mdl.pulse(task, 1) for task in EAST_vars if "kitting" in task.name]
        kitting_slots_WEST = [mdl.pulse(task, 1) for task in table_occupied_WEST]
        kitting_slots_WEST += [mdl.pulse(task, 1) for task in WEST_vars if "kitting" in task.name]

        mdl.add(mdl.sum(meca_resources) <= 3)
        mdl.add(mdl.sum(qc_resources) <= 1)
        mdl.add(mdl.sum(work_slots_EAST) <= 2)
        mdl.add(mdl.sum(work_slots_WEST) <= 2)
        mdl.add(mdl.sum(kitting_slots_EAST) <= 3)
        mdl.add(mdl.sum(kitting_slots_WEST) <= 3)

        [mdl.add(mdl.start_of(task) % 14*6 < 11*6) for task in all_tasks if "meca" in task.name]

        MS1_meca_qc = [task for task in MS1_vars if (("meca" in task.name) or ("qc" in task.name))]
        mdl.add(mdl.no_overlap(MS1_meca_qc))

        MS2_meca_qc = [task for task in MS2_vars if (("meca" in task.name) or ("qc" in task.name))]
        mdl.add(mdl.no_overlap(MS2_meca_qc))

        MS3_meca_qc = [task for task in MS3_vars if (("meca" in task.name) or ("qc" in task.name))]
        mdl.add(mdl.no_overlap(MS3_meca_qc))

        MS4_meca_qc = [task for task in MS4_vars if (("meca" in task.name) or ("qc" in task.name))]
        mdl.add(mdl.no_overlap(MS4_meca_qc))

        FOV_meca_qc = [task for task in FOV_vars if (("meca" in task.name) or ("qc" in task.name))]
        mdl.add(mdl.no_overlap(FOV_meca_qc))

        GTW_meca_qc = [task for task in GTW_vars if (("meca" in task.name) or ("qc" in task.name))]
        mdl.add(mdl.no_overlap(GTW_meca_qc))

        mdl.add(mdl.minimize(mdl.max([mdl.end_of(t) for t in all_tasks]) - mdl.min([mdl.start_of(t) for t in all_tasks])))

        return mdl

    def main(self, from_scratch, timeout, solution):
        mdl = self.create_model()
        if from_scratch:
            sol = self.solve(mdl, timeout)
            return sol
        else:
            mdl, stp = self.start_from_solution(mdl, solution)
            sol = self.solve(mdl, timeout)
            return sol

    def start_from_solution(self, mdl, solution):
        df = Solution.generate_Solution_from_json(solution)

        df2 = df[df.IsPresent == True]
        #print(np.asarray(df["Start"]))
        df2["Start"] = df2["Start"].apply(lambda a : date_converter.convert_to_work_time(a))
        df2["Finish"] = df2["Finish"].apply(lambda a : date_converter.convert_to_work_time(a))

        stp = mdl.create_empty_solution()
        print("BONJOUR")
        for var in mdl.get_all_variables():
            df3 = df2[df2.Task == var.name[-6:]]
            df3 = df3[df3.Part == var.name[:-6]].values
            if len(df3) >0 :
                #print(df3)
                df3 = df3[0]
                
                stp.add_interval_var_solution(var, df3[4], df3[1], df3[2] , df3[2] - df3[1], df3[2] - df3[1])
            
        stp.print_solution()
        # print("AUREVOIR")
        mdl.set_starting_point(stp)

        return mdl,df2


    def solve(self, mdl, timeout, strategy = 7, searchType = "Restart"):

        strategies = []
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(mdl.get_all_variables())))))]
        strategies += [mdl.search_phase(mdl.get_all_variables(),varchooser=mdl.select_random_var(),valuechooser = mdl.select_random_value())]
        
        mdl.add(strategies[strategy])
        msol = mdl.solve(TimeLimit = timeout, SearchType = searchType)
        msol.print_solution()
        
        solution = Solution.create_solution_from_PPC_result(msol.get_all_var_solutions())
        Solution.create_html_gantt_from_solution(solution, f"Solution_PPC_{timeout}_sec_{strategy}_type_{searchType}")
        Solution.generate_json_from_Solution(solution, f"Solution_PPC_{timeout}_sec_{strategy}_type_{searchType}")

        return solution


    def get_start(self, sol):
        return sol.get_start()


    def print_interval_vars_list(self, list):
        for i in range(len(list)):
            print(str(list[i]) + ", soit une durée de " + str(list[i].get_length()[0]/3600) + " heures")


    def print_OUEST(self):
        max_rows = None
        max_cols = None
        pd.set_option("display.max_rows", max_rows, "display.max_columns", max_cols)
        #print(self.timeOUEST)
        #print(self.timeOUEST.index)
        print(self.req_matOUEST)
        #print(self.req_taskOUEST)

    def print_EST(self):
        max_rows = None
        max_cols = None
        pd.set_option("display.max_rows", max_rows, "display.max_columns", max_cols)
        #print(self.timeEST)
        #print(self.req_matEST)
        #print(self.req_taskEST)


    #------------------------- FONCTIONS A CODER ---------------------------------------
    def maj_date_min_task(self, new_date_min, name_task):
        print("-----maj_date_min_task(new_date_min, name_task)-------")
        print("TODO")

    def maj_date_livraison(self, new_date_livraison, etiq_product):
        print("-----maj_date_livraison(new_date_livraison, etiq_product)------")
        print("TODO")
    #------------------------------------------------------------------------------------


    def apply_and_check_nouvelle_livraison(self, jour, mois, annee, etiq_product, path_solution):

        timeOUEST, req_matOUEST, req_taskOUEST = self.timeOUEST, self.req_matOUEST, self.req_taskOUEST
        #Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
        timeEST, req_matEST, req_taskEST = self.timeEST, self.req_matEST, self.req_taskEST
        #Extract_data.extract_tasks_from_excel(Extract_data.pathEST)
        
        last_solution = Solution.generate_Solution_from_json(path_solution)
        last_solution = last_solution[last_solution.IsPresent == True]
        
        need_solve_again = True

        date = datetime(annee,mois,jour)
        date_timestamp = datetime.timestamp(date)

        #dates des livraisons
        livraisons = (pd.read_excel("./data/livraison guides.xlsx",parse_dates=['livraison au MAG AIT'])).iloc[:,2:]

        #---------------- recherche date originale ----------------
        found = False
        size = len(livraisons["Etiquettes TOPO"])
        date_origin = date
        for i in range(size):
            l = livraisons["Etiquettes TOPO"][i]
        
            if (l == etiq_product):
                found = True
                date_origin = livraisons["livraison au MAG AIT"][i]
                #print(type(date_origin))
                #<class 'pandas._libs.tslibs.timestamps.Timestamp'>
                #<=> datetime !!

                # maj date livraison ==============================================================================
                self.maj_date_livraison(date, etiq_product) #TODO
                # modif d'un json sur BDD ? => changer la récupération des livraisons juste au dessus !!

        #---------------- vérification écart date ----------------
        plus_tot = False
        plus_tard = False

        if not(found):
            print("problème - référence pas trouvée")
            need_solve_again = False
            #cas où len(livraisons) == 0 : ici
        else:
            livraison_before_origin = date < date_origin
            livraison_equals_origin = (date == date_origin)
            if (livraison_equals_origin): 
                print("date livraison non changée")
                need_solve_again = False
            elif(livraison_before_origin):
                print("date livraison plut tôt que prévu")
                plus_tot = True
            else:
                print("date livraison plut tard que prévu")
                plus_tard = True
        
        #---------------- recherche tâches + min dates tâches ----------------
        found_tasks_EST = False
        num_EST = 0
        tasks_EST_i = []
        tasks_EST = []
        dates_min_EST = []

        found_tasks_OUEST = False
        num_OUEST = 0
        tasks_OUEST_i = []
        tasks_OUEST = []
        dates_min_OUEST = []

        if need_solve_again:
            print("---------------- recherche tâches + min dates tâches ----------------")

            #---------------- recherche EST
            for i in range(len(req_matEST)):
                task = req_matEST.index[i]
                liste_produits_livraison = req_matEST.iloc[i,0]
                min_start_date = req_matEST.iloc[i,2]

                if etiq_product in liste_produits_livraison:
                    print("ok EST : task = ", task)
                    found_tasks_EST = True
                    tasks_EST_i.append(i)
                    tasks_EST.append(task)
                    dates_min_EST.append(min_start_date)

            #---------------- recherche OUEST
            for i in range(len(req_matOUEST)):
                task = req_matOUEST.index[i]
                liste_produits_livraison = req_matOUEST.iloc[i,0]
                min_start_date = req_matOUEST.iloc[i,2]

                if etiq_product in liste_produits_livraison:
                    print("ok OUEST : task = ", task)
                    found_tasks_OUEST = True
                    tasks_OUEST_i.append(i)
                    tasks_OUEST.append(task)
                    dates_min_OUEST.append(min_start_date)

            num_EST = len(tasks_EST_i)
            num_OUEST = len(tasks_OUEST_i)

            found_tasks = found_tasks_EST or found_tasks_OUEST
            if (not found_tasks):
                print("problème - aucune tâche trouvée pour la référence")
                need_solve_again = False
        
        #---------------- vérification min dates ----------------
        #si plus tard 
        #toutes les taches ont un min superieur a date => rien a faire
        #une des taches a un min inferieur a date => min de cette tache a maj + solve again

        #recherche un min de tache < date
        found_min_inf = False
        list_tasks_min_inf = []

        if need_solve_again and plus_tard:
            print("---------------- vérification min dates ----------------\n si plus tard")

            if found_tasks_EST:
                for i in range(num_EST):
                    current_date = dates_min_EST[i]
                    if current_date < date:
                        #maj min (:= date) de la tache d'index tasks_EST_i[i] et de nom tasks_EST[i] ======================
                        self.maj_date_min_task(date, tasks_EST[i]) #TODO
                        found_min_inf = True
                        list_tasks_min_inf.append(tasks_EST[i])
        
            if found_tasks_OUEST:
                for i in range(num_OUEST):
                    current_date = dates_min_OUEST[i]
                    if current_date < date:
                        #maj min (:= date) de la tache d'index tasks_OUEST_i[i] et de nom tasks_OUEST[i] ==================
                        self.maj_date_min_task(date, tasks_OUEST[i]) #TODO
                        found_min_inf = True
                        list_tasks_min_inf.append(tasks_OUEST[i])
            
            if (not found_min_inf):
                print("tâches trouvées pour la référence : déjà une date min supérieure")
                need_solve_again = False
        
        #si plus tot
        #toutes les taches ont un min superieur a origin => rien a faire
        #une des taches a un min egal a origin  => recalcul du min de cette tache avec autre produits : si une amélioration => solve again
        if need_solve_again and plus_tot:
            print("---------------- vérification min dates ----------------\n si plus tot")

            #recherche un min de tache == date_origin améliorant !
            found_min_mieux = False

            if found_tasks_EST:
                for i in range(num_EST):
                    current_task = tasks_EST[i]
                    current_num_task = tasks_EST_i[i]
                    current_date = dates_min_EST[i]
                    liste_produits_current_task = req_matEST.iloc[current_num_task,0]

                    if current_date == date_origin:
                        
                        #recalcul : est-ce que date_origin dependait uniquement du produit changé ?
                        max_livraison = date
                        for ref,date_liv in livraisons.iloc[:].values:
                            if ref in liste_produits_current_task:
                                if date_liv > max_livraison:
                                    max_livraison = date_liv

                        if max_livraison < date_origin:
                            #maj min (:= max_livraison) de la tache d'index current_num_task et de nom current_task ======================
                            self.maj_date_min_task(max_livraison, current_task) #TODO
                            found_min_mieux = True
        
            if found_tasks_OUEST:
                for i in range(num_OUEST):
                    current_task = tasks_OUEST[i]
                    current_num_task = tasks_OUEST_i[i]
                    current_date = dates_min_OUEST[i]
                    liste_produits_current_task = req_matOUEST.iloc[current_num_task,0]

                    if current_date == date_origin:
                        
                        #recalcul : est-ce que date_origin dependait uniquement du produit changé ?
                        max_livraison = date
                        for ref,date_liv in livraisons.iloc[:].values:
                            if ref in liste_produits_current_task:
                                if date_liv > max_livraison:
                                    max_livraison = date_liv

                        if max_livraison < date_origin:
                            #maj min (:= max_livraison) de la tache d'index current_num_task et de nom current_task ======================
                            self.maj_date_min_task(max_livraison, current_task) #TODO
                            found_min_mieux = True
            
            if (not found_min_mieux):
                print("tâches trouvées pour la référence : toutes avec un autre produit de date min supérieure")
                need_solve_again = False
            
        #---------------- vérification start dates ----------------
        #si plus tot && une des taches a un min egal a origin && amélioration du min => solve again (deja prévu)
        
        #si plus tard && une des taches a un min inferieur a date => min de cette tache a maj 
        # => si ces taches demarraient avant cette date : solve again

        # pd.DataFrame(columns = ["Task", "Start","Finish", "Part","IsPresent"] )

        if need_solve_again and plus_tard and found_min_inf:
            
            sol_tasks_to_check = last_solution[last_solution.Task.isin(list_tasks_min_inf)]

            sol_tasks_inf = sol_tasks_to_check[sol_tasks_to_check.Start <= date_timestamp*1000]
        
            starts_task_found = (len(sol_tasks_inf.Start) != 0)
            
            if (not starts_task_found):
                print("tâches trouvées pour la référence, dont la contrainte de départ est impactée : aucune ne démarre avant cette nouvelle date")
                need_solve_again = False

        return need_solve_again
    
    
        
    
        