from src.holidays import end_date_calc
from src.solver import resourceOrder
from src.resource import Resource, Rtype
from src.module import Module
from src.bloc import Bloc
from src.work import Work
import pandas as pd
import math
import os
from src.task import Task, State
import datetime

# Build a first version of solution
# Assume that time is continuous (no stop, no weekend, ...)
# Use only ten 10 first tasks of each block
# Assume that we have 3 meca ressources and 1 oc

PATH = os.path.abspath(os.getcwd()) + "/data/"
ms1_data = pd.read_excel(PATH + "ms1.xlsx")
ms2_data = pd.read_excel(PATH + "ms2.xlsx")
ms3_data = pd.read_excel(PATH + "ms2.xlsx")
fov_data = pd.read_excel(PATH + "fov.xlsx")
gtw_data = pd.read_excel(PATH + "gtw.xlsx")
ms4_data = pd.read_excel(PATH + "ms4.xlsx")

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
        task.min_start = row['date']
        tasks.append(task)
    for index, row in data.iterrows():
        if str(row['next']) != "nan":
            tasks[index].next = []
            names = row['next'].replace(" ", "").split(',')
            print(names)
            tasks[index].next.extend(list(filter(lambda t: t.name in names, tasks)))
        if str(row['prec']) != "nan":
            tasks[index].previous = []
            names = row['prec'].replace(" ", "").split(',')
            tasks[index].previous.extend(list(filter(lambda t: t.name in names, tasks)))
    for t in tasks:
        t.pending_prec = len(t.previous)
    return tasks


ms1_tasks = df2task(ms1_data, ms1)
ms2_tasks = df2task(ms2_data, ms2)
ms3_tasks = df2task(ms3_data, ms3)
ms4_tasks = df2task(ms4_data, ms4)
fov_tasks = df2task(fov_data, fov)
gtw_tasks = df2task(gtw_data, gtw)

#Gérer le cas F0V10 qui est lié à une autre tâche du même module

#get max_date
max_date = datetime.datetime(year=2018, month=1, day=1)
for i in ms1_tasks + ms2_tasks + ms3_tasks + ms4_tasks + fov_tasks + gtw_tasks:
    if i.min_start > max_date:
        max_date = i.min_start

# Init ressources
mecanics = [Resource("r1", Rtype.meca), Resource("r2", Rtype.meca), Resource('r3', Rtype.meca)]
control = Resource("r1", Rtype.oc)
for operator in mecanics:
    operator.next_freeTime = max_date
control.next_freeTime = max_date


print(ms1_tasks[0])
# la liste des tâche à faire
works = [Work(ms1_tasks.pop(0)), Work(ms2_tasks.pop(0)), Work(ms3_tasks.pop(0)), Work(ms4_tasks.pop(0)),
        Work(fov_tasks.pop(0)), Work(gtw_tasks.pop(0))]
for w in works:
    w.meca_start = max_date
solution = []
i = 0
meca_w = 0
oc_w = 0
solution = []
while len(works) != 0:
    i = i+1
    # max: 2 resource by module -- non prise en compte
    # max: 3 kitting -- non prise en compte
    # Juste les tâches ayant besoin d'une opération de meca
    await_meca = list(filter(lambda w: w.task.state == State.not_started, works))
    await_meca.sort(key = lambda x: x.meca_start)
    mecanics.sort( key = lambda x: x.next_freeTime)
    if len(await_meca) > 0:
        await_meca[0].do_meca(mecanics[0])
        meca_w = meca_w +1
    await_oc = list(filter(lambda w: w.task.state == State.meca, works))
    #print(i, meca_w, oc_w)
    await_oc.sort(key = lambda x: x.oc_start)
    if len(await_oc) > 0:
        work = await_oc[0]
        work.do_oc(control)
        oc_w = oc_w +1
        # Ajout des prochaines tâche mais attention 1 tâche peuvent avoir plusieurs précédents
        # Dans ce cas ça marche plus
        for t in work.task.next:
            if t.pending_prec == 0:
                w = Work(t)
                w.meca_start = end_date_calc(work.oc_start, datetime.timedelta(hours=work.task.oc))
                works.append(w)
        # Remove the task done
        works.remove(work)
        solution.append(work)
for sol in solution:
    print(sol)
# Build a solution based on ResourceOrder solution of jobshop
# Solve it
# Display solution
