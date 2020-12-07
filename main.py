from src.solver import resourceOrder
from src.resource import Resource, rType
from src.module import Module
from src.bloc import Bloc
import pandas as pd
import math
import os
from src.task import Task

# Build a first version of solution
# Use integer instead of dates (start = 0)
# Assume that time is continuous (no stop, no weekend, ...)
# Unit of time minute
# Use only ten 10 first tasks of each block
# Assume that we have 3 meca ressources and 1 oc

ms1_data = pd.read_excel("/Users/paul/Documents/5ir/projet Intégrateur/planificateur/data/ms1.xlsx")
ms2_data = pd.read_excel("/Users/paul/Documents/5ir/projet Intégrateur/planificateur/data/ms2.xlsx")
ms3_data = pd.read_excel("/Users/paul/Documents/5ir/projet Intégrateur/planificateur/data/ms2.xlsx")
fov_data = pd.read_excel("/Users/paul/Documents/5ir/projet Intégrateur/planificateur/data/fov.xlsx")
gtw_data = pd.read_excel("/Users/paul/Documents/5ir/projet Intégrateur/planificateur/data/gtw.xlsx")
ms4_data = pd.read_excel("/Users/paul/Documents/5ir/projet Intégrateur/planificateur/data/ms4.xlsx")

est = Module("EST")
ouest = Module("OUEST")
ms1 = Bloc("MS1", ouest)
ms2 = Bloc("MS2", est)
ms3 = Bloc("MS3", est)
ms4 = Bloc("MS4", ouest)
fov = Bloc("FOV", est)
gtw = Bloc("GTW", ouest)

def df2task(data, bloc):
    tasks = []
    for index, row in data.iterrows():
        task = Task(name=row['Task_id'], bloc=bloc, meca=row['meca'], oc=row['oc'])
        tasks.append(task)
    for index, row in data.iterrows():
        if str(row['next']) != "nan":
            tasks[index].next = []
            names = row['next'].split(',')
            tasks[index].next.extend(list(filter(lambda t: t.name in names, tasks)))
    return tasks


ms1_tasks = df2task(ms1_data, ms1)
ms3_tasks = df2task(ms2_data, ms2)
ms3_tasks = df2task(ms3_data, ms3)
ms4_tasks = df2task(ms4_data, ms4)
fov_tasks = df2task(fov_data, fov)
gtw_tasks = df2task(gtw_data, gtw)

r = [Resource("r1", rType.oc), Resource("r2", rType.meca), Resource("r3", rType.meca), Resource('r4', rType.meca)]

#Build a solution based on ResourceOrder solution of jobshop
# Solve it

# Display solution
