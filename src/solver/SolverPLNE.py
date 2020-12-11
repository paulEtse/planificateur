from extractor import Extract_data
#from src import SolverInterface
import numpy as np
import pandas as pd

from datetime import date, datetime, timedelta
from docplex.mp.model import Model


#class SolverPLNE(): #SolverInterface
def solve_from_skratch():
    """
    Load all constraints and find and acceptable solution 
    """
    model = get_basic_problem()
    model = add_additional_contraints(model)
    sol = model.solve()
    print(model.get_solve_status())
    return(sol)


def Solve_from_solution(s):
    """ 
        Load all constraints starts form s find and acceptable solution
    """
    # TODO
    

def add_additional_contraints(model) -> Model:
    """
    add all unextected additional contraints 
    """
    # add additional unexpected contstaints
    # TODO
    return(model)

def get_basic_problem() -> Model:
    """
        returns the PLNE problem without any unknown factors
    """
    
    timeOUEST, req_matOUEST, req_taskOUEST = Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
    timeEST, req_matEST, req_taskEST = Extract_data.extract_tasks_from_excel(Extract_data.pathEST)
    time = pd.concat([timeOUEST,timeEST])
    print(time)
    time["task"] = (time.index).map(lambda x: x[:3])
    req_mat = pd.concat([req_matOUEST,req_matEST])
    req_task = pd.concat([req_taskOUEST,req_taskEST])
    model = Model("My model")
    model.log_output = True
    time_size = int(60*7*60*2/10) #max 90 jours * 7 h par jours * 60 min * 2 shifts / 10 min (= un grain) #
    Meca_X = np.asarray(list(model.binary_var_matrix(len(time.index),time_size).values())).reshape(len(time.index),time_size) #a une date donnèe une tache est en cours si elle a la valeure 1 dans cette matrice 
    # print(np.asarray(Meca_X))
    # Meca_X = pd.DataFrame(Meca_X)
    # print(Meca_X)  
    Control_X = np.asarray(list(model.binary_var_matrix(len(time.index),time_size).values())).reshape(len(time.index),time_size) #a une date donnèe une tache est en cours si elle a la valeure 1 dans cette matrice 
    Kitting_X = np.asarray(list(model.binary_var_matrix(len(time.index),time_size).values())).reshape(len(time.index),time_size) #a une date donnèe une tache est en cours si elle a la valeure 1 dans cette matrice
    kitting_time = int(3*60/10) #3h * 60 minutes / 10 (= un grain)
    N = len(time.index) #taille des matrices ci-dessus

    
    
    # add basic constraints
    for i in range(0,N): #contrintes sur les lignes
        print(time.index[i])
        model.add_constraint(model.sum(Kitting_X[i]) == kitting_time) # un kitting prends 3 h
        model.add_constraint(model.sum(Meca_X[i]) == time.iloc[i,2]) # une tache meca prends excatement le temps necessaire
        model.add_constraint(model.sum(Control_X[i]) == time.iloc[i,3]) #une tache QC prends excatement le temps necessaire
        for j in range(0,time_size):
            model.add_if_then(Meca_X[i,j]== True, model.sum(Kitting_X[i,range(j,time_size)]) == 0) # une tache meca s'effectue apres son kitting
            model.add_if_then(Control_X[i,j] == True, model.sum(Meca_X[i,range(j,time_size)]) == 0) # une tache controle s'effecture apres sa mecanique
            if len(req_task.iloc[i].values[0] )!= 0 :
                #print(len(req_task.iloc[i].values[0]))
                for task in req_task.iloc[i].values[0]:
                    #print(req_task.iloc[i],task,list(time.index),list(time.index).index(str(task)),i,range(j,time_size))
                    model.add_if_then(Control_X[list(time.index).index(str(task)),j] == True, model.sum(Meca_X[i,range(j,time_size)]) == 0)  #une tache demarre apres la fin de toutes les taches necessaire pour la realiser
            
        model.add_constraint(model.sum(Kitting_X[i,range(0,get_time(req_mat.iloc[i,2]))]) == 0)  # le debut d'une tache de kitting ne peut s'effectuer que lorsque tous le materiel est livré
       



    for i in range(0,time_size):
        model.add_constraint(model.sum(Meca_X[:,i]) + model.sum(Kitting_X[:,i]) <= 3) # pas plus de 3 mecha par shift
        model.add_constraint(model.sum(Control_X[:,i]) <= 1) # pas plus d'un QC par shift
        model.add_constraint(model.sum(Meca_X[range(0,len(timeOUEST.index))]) + model.sum(Control_X[range(0,len(timeOUEST.index))]) <= 2) # pas plus de deux mecha sur le coté ouest
        model.add_constraint(model.sum(Meca_X[range(len(timeOUEST.index),len(timeOUEST.index) + len(timeEST.index))]) + model.sum(Control_X[range(len(timeOUEST.index),len(timeOUEST.index) + len(timeEST.index))]) <= 2) # pas plus de deux mecha sur le coté est
        model.add_constraints([         # pas deux taches en meme temps sur le meme poste
            Meca_X[time.task == "MS1"].sum() == 1,
            Meca_X[time.task == "MS2"].sum() == 1,
            Meca_X[time.task == "MS3"].sum() == 1,
            Meca_X[time.task == "MS4"].sum() == 1,
            Meca_X[time.task == "FOV"].sum() == 1,
            Meca_X[time.task == "GTW"].sum() == 1])

    #TODO pas plus de 3 kitting prets en meme temps
    #TODO ne pas commancer une tache meca moins de 3h avant la fin d'une journee 
    #TODO kitting en parallele

    #set objective
    begin = np.min([np.min(np.nonzero(Kitting_X[i])) for i in range(0,N)])
    end = np.max(([np.max(np.nonzero(Control_X[i])) for i in range(0,N)]))
    model.set_objective("min",end-begin)

    return(model)

def get_time(date_input):
    """
        DESCRIPTION
    """
    #TODO virrer les week-end et les jours feriers
    ref = datetime(2019,11,1,0,0,0)
    date_input = date_input.to_pydatetime()
    if date_input < ref :
        return 0
    else :
        if date_input > ref + timedelta(days=60):
            return(int(60*7*60*2/10) -1)
        else:
            delta = (date_input - ref)
            return(int(delta.days*420*2/10))