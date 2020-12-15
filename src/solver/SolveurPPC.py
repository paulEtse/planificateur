#import SolverInterface
from docplex.cp.modeler import end_before_start
from docplex.cp.model import CpoModel, CpoStepFunction, INTERVAL_MIN, INTERVAL_MAX
import docplex.cp.utils_visu as visu
import os
from extractor import Extract_data
from src import Solution
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
        self.start_date = pd.Timestamp(year = 2019, month = 12, day = 12)
        self.max_end_timestamp = int(self.convert_to_absolute_time(pd.Timestamp(year = 2020, month = 1, day = 15)))
        self.kitting_time_max = 3 * 3600
        self.kitting_time_mid = int(1.5 * 3600)
        self.kitting_time_min = 3600
        pio.renderers.default = "vscode"
  
    def solve_from_skratch(self):
        print("")

    def print_gantt(self, solution):
        pass

    # def run_server(self, 
    #             port=8050, 
    #             debug=False, 
    #             threaded=True, 
    #             **flask_run_options): 
    #     self.server.run(port=port, debug=debug, **flask_run_options) 

    
              
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

        kits_pulse_for_choice = []
        for i in range(len(self.timeOUEST)):
            #min_start_time = int(max(0, self.convert_to_absolute_time(self.req_matOUEST.iloc[i,2])))
            min_start_time = int(self.convert_to_absolute_time(self.req_matOUEST.iloc[i,2]))
            meca_length = self.timeOUEST.iloc[i, 2] * 60
            qc_length = self.timeOUEST.iloc[i, 3] * 60

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

            mdl.add(mdl.end_before_start(kit_interval, meca_interval))
            mdl.add(mdl.end_before_start(meca_interval, qc_interval))

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
        for i in range(len(self.timeEST)):
            #min_start_time = int(max(0, self.convert_to_absolute_time(self.req_matEST.iloc[i,2])))
            min_start_time = int(self.convert_to_absolute_time(self.req_matEST.iloc[i,2]))
            meca_length = self.timeEST.iloc[i, 2] * 60
            qc_length = self.timeEST.iloc[i, 3] * 60
            
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

            mdl.add(mdl.end_before_start(kit_interval, meca_interval))
            mdl.add(mdl.end_before_start(meca_interval, qc_interval))

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

        kitting_slots_EAST = [mdl.pulse(task, 1) for task in EAST_vars if "kitting" in task.name]
        kitting_slots_WEST = [mdl.pulse(task, 1) for task in WEST_vars if "kitting" in task.name]

        mdl.add(mdl.sum(meca_resources) <= 3)
        mdl.add(mdl.sum(qc_resources) <= 1)
        mdl.add(mdl.sum(work_slots_EAST) <= 2)
        mdl.add(mdl.sum(work_slots_WEST) <= 2)
        mdl.add(mdl.sum(kitting_slots_EAST) <= 3)
        mdl.add(mdl.sum(kitting_slots_WEST) <= 3)

        [mdl.add(mdl.start_of(task) % 50400 < 39600) for task in all_tasks if "meca" in task.name]
        [mdl.add(mdl.start_of(task) % 50400 >= 0) for task in all_tasks if "meca" in task.name]

        mdl.add(mdl.minimize(mdl.max([mdl.end_of(t) for t in all_tasks]) - mdl.min([mdl.start_of(t) for t in all_tasks])))

        print(mdl.export_model())

        #print(mdl.refine_conflict())
        #print("Solving model....")
        msol = mdl.solve(FailLimit = 1000000, TimeLimit = 10)#, agent='local', execfile='C:\\Program Files\\IBM\\ILOG\\CPLEX_Studio1210\\cpoptimizer\\bin\\x64_win64\\cpoptimizer')
        #print("Solution: ")
        #msol.print_solution()

        intervals = msol.get_all_var_solutions()
        intervals = [solution for solution in intervals if solution.is_present()]

        sol = pd.DataFrame(index = [s.get_name() for s in intervals], columns = ["Task", "Start_time", "End_time", "Operator"])

        intervals.sort(key = self.get_start)

        for ind in sol.index:
            sol.loc[ind, "Task"] = ind
            sol.loc[ind, "Operator"] = []

        print(sol)
        
        next_time_free = [0, 0, 0, 0]
        for solution in intervals:
            name = solution.get_name()
            if "kitting" in name:
                k = 0
                if "1 op" in name:
                    while(k < 1):
                        for i in range(len(next_time_free) - 1):
                            if next_time_free[i] <= solution.get_start():
                                sol.loc[name, "Start_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_start()))
                                sol.loc[name, "End_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_end()))
                                sol.loc[name, "Operator"].extend([i])
                                break
                        k += 1
                if "2 op" in name:
                    while(k < 2):
                        for i in range(len(next_time_free) - 1):
                            if next_time_free[i] <= solution.get_start():
                                sol.loc[name, "Start_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_start()))
                                sol.loc[name, "End_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_end()))
                                sol.loc[name, "Operator"].extend([i])
                                break
                        k += 1
                if "3 op" in name:
                    while(k < 3):
                        for i in range(len(next_time_free) - 1):
                            if next_time_free[i] <= solution.get_start():
                                sol.loc[name, "Start_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_start()))
                                sol.loc[name, "End_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_end()))
                                sol.loc[name, "Operator"].extend([i])
                                break
                        k += 1
            elif "meca" in name:
                    for i in range(len(next_time_free) - 1):
                        if next_time_free[i] <= solution.get_start():
                            sol.loc[name, "Start_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_start()))
                            sol.loc[name, "End_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_end()))
                            sol.loc[name, "Operator"].extend([i])
                            break
            else:
                sol.loc[name, "Start_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_start()))
                sol.loc[name, "End_time"] = datetime.fromtimestamp(self.convert_to_normal_time(solution.get_end()))
                sol.loc[name, "Operator"].extend([4])

        print(sol)

        # # fig = ff.create_gantt(sol)
        # # fig.show()

        # fig = px.timeline(sol, x_start="Start_time", x_end="End_time", y="Task")
        # fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
        # fig.show()

        # df = pd.DataFrame([
        #     dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28'),
        #     dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15'),
        #     dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30')
        # ])

        # fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task")
        # fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
        # fig.show()

        fig = px.timeline(sol, x_start="Start_time", x_end="End_time", y="Operator")
        fig.update_yaxes(autorange="reversed")
        fig.write_image("../fig1.pdf")


    def get_start(self, sol):
        return sol.get_start()


    def print_interval_vars_list(self, list):
        for i in range(len(list)):
            print(str(list[i]) + ", soit une durée de " + str(list[i].get_length()[0]/3600) + " heures")

    def convert_to_absolute_time(self, timestamp):
        #print(timestamp)
        #print(self.start_date)
        #print(timestamp.timestamp() - self.start_date.timestamp())
        return timestamp.timestamp() - self.start_date.timestamp()

    def convert_to_normal_time(self, timestamp):

        return timestamp + self.start_date.timestamp()

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
        

        