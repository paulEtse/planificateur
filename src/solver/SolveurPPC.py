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
from datetime import datetime
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio

class SolveurPPC:  
    def __init__(self):
        self.timeOUEST, self.req_matOUEST, self.req_taskOUEST = Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
        self.timeEST, self.req_matEST, self.req_taskEST = Extract_data.extract_tasks_from_excel(Extract_data.pathEST)
        self.start_date = datetime.timestamp(datetime(2019,12,1))
        self.max_end_timestamp = date_converter.convert_to_work_time(datetime.timestamp(datetime(2020,3,15)))
        self.kitting_time_max = 3 * 6
        self.kitting_time_mid = int(1.5 * 6)
        self.kitting_time_min = 6
        pio.renderers.default = "vscode"

    def solve_from_skratch(self):
        print("")

    def print_gantt(self, solution):
        pass


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
            #min_start_time = int(max(0, date_converter.convert_to_work_time(self.req_matOUEST.iloc[i,2])))
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

            # mdl.add(mdl.end_before_start(kit_interval1mec, meca_interval))
            # mdl.add(mdl.end_before_start(kit_interval2mec, meca_interval))
            # mdl.add(mdl.end_before_start(kit_interval3mec, meca_interval))

            table_slot_occupied_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = (0, 9999999999999), name = "Table occupied " + self.timeOUEST.index[i])
            table_occupied_WEST += [table_slot_occupied_interval]

            mdl.add(mdl.end_before_start(kit_interval, meca_interval))
            mdl.add(mdl.end_before_start(meca_interval, qc_interval))

            mdl.add(mdl.start_at_end(table_slot_occupied_interval, kit_interval))
            mdl.add(mdl.start_at_end(meca_interval, table_slot_occupied_interval))

            # WEST_vars += [kit_interval1mec]
            # WEST_vars += [kit_interval2mec]
            # WEST_vars += [kit_interval3mec]
            
            WEST_vars += [kit_interval]
            WEST_vars += [meca_interval]
            WEST_vars += [qc_interval]

            if i < 19:

                # MS1_vars += [kit_interval1mec]
                # MS1_vars += [kit_interval2mec]
                # MS1_vars += [kit_interval3mec]

                MS1_vars += [kit_interval]
                MS1_vars += [meca_interval]
                MS1_vars += [qc_interval]

            elif i >= 45:

                # GTW_vars += [kit_interval1mec]
                # GTW_vars += [kit_interval2mec]
                # GTW_vars += [kit_interval3mec]

                GTW_vars += [kit_interval]
                GTW_vars += [meca_interval]
                GTW_vars += [qc_interval]
            
            else:

                # MS4_vars += [kit_interval1mec]
                # MS4_vars += [kit_interval2mec]
                # MS4_vars += [kit_interval3mec]

                MS4_vars += [kit_interval]
                MS4_vars += [meca_interval]
                MS4_vars += [qc_interval]

        # self.print_interval_vars_list(MS1_vars)
        # print("#################################")
        # self.print_interval_vars_list(MS4_vars)
        # print("#################################")
        # self.print_interval_vars_list(GTW_vars)


        ######################################################
        # Creating interval variables for EAST module
        ######################################################
        FOV_vars = []
        MS2_vars = []
        MS3_vars = []
        EAST_vars = []
        table_occupied_EAST = []

        for i in range(len(self.timeEST)):
            #min_start_time = int(max(0, date_converter.convert_to_work_time(self.req_matEST.iloc[i,2])))
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

            # mdl.add(mdl.end_before_start(kit_interval1mec, meca_interval))
            # mdl.add(mdl.end_before_start(kit_interval2mec, meca_interval))
            # mdl.add(mdl.end_before_start(kit_interval3mec, meca_interval))

            table_slot_occupied_interval = mdl.interval_var(start = (min_start_time, self.max_end_timestamp), length = (0, 9999999999999), name = "Table occupied " + self.timeEST.index[i])
            table_occupied_EAST += [table_slot_occupied_interval]

            mdl.add(mdl.end_before_start(kit_interval, meca_interval))
            mdl.add(mdl.end_before_start(meca_interval, qc_interval))

            mdl.add(mdl.start_at_end(table_slot_occupied_interval, kit_interval))
            mdl.add(mdl.start_at_end(meca_interval, table_slot_occupied_interval))

            # EAST_vars += [kit_interval1mec]
            # EAST_vars += [kit_interval2mec]
            # EAST_vars += [kit_interval3mec]

            EAST_vars += [kit_interval]
            EAST_vars += [meca_interval]
            EAST_vars += [qc_interval]
            
            if i < 11:
               
                # FOV_vars += [kit_interval1mec]
                # FOV_vars += [kit_interval2mec]
                # FOV_vars += [kit_interval3mec]

                FOV_vars += [kit_interval]
                FOV_vars += [meca_interval]
                FOV_vars += [qc_interval]

            elif i >= 25:

                # MS3_vars += [kit_interval1mec]
                # MS3_vars += [kit_interval2mec]
                # MS3_vars += [kit_interval3mec]

                MS3_vars += [kit_interval]
                MS3_vars += [meca_interval]
                MS3_vars += [qc_interval]

            else:

                # MS2_vars += [kit_interval1mec]
                # MS2_vars += [kit_interval2mec]
                # MS2_vars += [kit_interval3mec]

                MS2_vars += [kit_interval]
                MS2_vars += [meca_interval]
                MS2_vars += [qc_interval]

        # self.print_interval_vars_list(FOV_vars)
        # print("#################################")
        # self.print_interval_vars_list(MS2_vars)
        # print("#################################")
        # self.print_interval_vars_list(MS3_vars)

        ##################################################
        # Setting requirement relations between interval variables
        ##################################################
        for task in MS1_vars:
            for i in range(len(self.req_taskOUEST)):
                if (self.req_taskOUEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskOUEST.iloc[i, 0])):
                        for other_task in WEST_vars:
                            if self.req_taskOUEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                #print(task.name + " doit commencer après la fin de " + other_task.name)
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in MS4_vars:
            for i in range(len(self.req_taskOUEST)):
                if (self.req_taskOUEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskOUEST.iloc[i, 0])):
                        for other_task in WEST_vars:
                            if self.req_taskOUEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                #print(task.name + " doit commencer après la fin de " + other_task.name)
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in GTW_vars:
            for i in range(len(self.req_taskOUEST)):
                if (self.req_taskOUEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskOUEST.iloc[i, 0])):
                        for other_task in WEST_vars:
                            if self.req_taskOUEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                #print(task.name + " doit commencer après la fin de " + other_task.name)
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in MS2_vars:
            for i in range(len(self.req_taskEST)):
                if (self.req_taskEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskEST.iloc[i, 0])):
                        for other_task in EAST_vars:
                            if self.req_taskEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                #print(task.name + " doit commencer après la fin de " + other_task.name)
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in MS3_vars:
            for i in range(len(self.req_taskEST)):
                if (self.req_taskEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskEST.iloc[i, 0])):
                        for other_task in EAST_vars:
                            if self.req_taskEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                #print(task.name + " doit commencer après la fin de " + other_task.name)
                                mdl.add(mdl.end_before_start(other_task, task))
        #print("##############################################")
        for task in FOV_vars:
            for i in range(len(self.req_taskEST)):
                if (self.req_taskEST.index[i] in task.name) and "meca" in task.name:
                    for j in range(len(self.req_taskEST.iloc[i, 0])):
                        for other_task in EAST_vars:
                            if self.req_taskEST.iloc[i, 0][j] in other_task.name and "qc" in other_task.name:
                                #print(task.name + " doit commencer après la fin de " + other_task.name)
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
        #[mdl.add(mdl.start_of(task) % 14*6 >= 0) for task in all_tasks if "meca" in task.name]

        mdl.add(mdl.no_overlap(MS1_vars))
        mdl.add(mdl.no_overlap(MS2_vars))
        mdl.add(mdl.no_overlap(MS3_vars))
        mdl.add(mdl.no_overlap(MS4_vars))
        mdl.add(mdl.no_overlap(FOV_vars))
        mdl.add(mdl.no_overlap(GTW_vars))

        mdl.add(mdl.minimize(mdl.max([mdl.end_of(t) for t in all_tasks]) - mdl.min([mdl.start_of(t) for t in all_tasks])))

        print(mdl.export_model())

        strategies = []
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_impact()))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_impact()))]

        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.domain_size()),valuechooser = mdl.select_largest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_smallest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_smallest(mdl.value_index(range(len(all_tasks)))))]
        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_largest(mdl.var_local_impact()),valuechooser = mdl.select_largest(mdl.value_index(range(len(all_tasks)))))]

        strategies += [mdl.search_phase(all_tasks,varchooser=mdl.select_random_var(),valuechooser = mdl.select_random_value())]

        #print(mdl.refine_conflict())
        #print("Solving model....")
        time = 15
        params = CpoParameters(TimeLimit=time, LogPeriod=100000, SearchType="DepthFirst")
        mdl.add_search_phase(strategies[7])

        df = Solution.generate_Solution_from_json("./Solution_PPC_15_sec.json")
        
        df2 = df[df.IsPresent == True]

        print(df)
        print(df2)
        df2["Start"] = df2["Start"].apply(lambda a : date_converter.convert_to_work_time(int(a/1000)))
        df2["Finish"] = df2["Finish"].apply(lambda a : date_converter.convert_to_work_time(int(a/1000)))

        print(df2)

        # stp = mdl.create_empty_solution()
        # for var in all_tasks:
        #     stp[var] = 

        # msol = mdl.solve(TimeLimit = time)#, agent='local', execfile='C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio1210\\cpoptimizer\\bin\\x64_win64\\cpoptimizer')
        # #msol = run(mdl, params)
        # #print("Solution: ")
        # msol.print_solution()
        
        

        solution = Solution.create_solution_from_PPC_result(msol.get_all_var_solutions())
        print(solution)
        Solution.create_html_gantt_from_solution(solution, f"Solution_PPC_{time}_sec")
        Solution.generate_json_from_Solution(solution, f"Solution_PPC_{time}_sec")


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
        

        