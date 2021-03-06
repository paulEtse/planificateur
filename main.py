# coding=utf-8

from src.resource import Resource, Rtype
from src.module import Module
from src.bloc import Bloc
import pandas as pd
import numpy as np
from src.date_converter import end_date_calc, start1_of_date
from src.task import Task, State
import datetime
from extractor.Extract_data import pathOUEST, pathEST, extract_tasks_from_excel, add_next2req_task


# Build a first version of solution
# Assume that we have 3 meca ressources and 1 oc

def makespan(solution):
    start_date = solution[0].kitting_start
    end_date = solution[0].oc_end
    for t in solution:
        if start_date > t.kitting_start:
            start_date = t.kitting_start
        if end_date < t.oc_end:
            end_date = t.oc_end
    # print(start_date, end_date)
    return end_date - start_date


def do_best_meca_using_req(tasks, meca):
    raise NotImplemented


def choose_best_oc_task(tasks, control):
    # Task that can be done
    filtered_tasks = list(filter(lambda t: t.block.module.can_work(max(t.oc_start, control.next_freeTime),
                                                                   end_date_calc(max(t.oc_start, control.next_freeTime),
                                                                                 datetime.timedelta(
                                                                                     minutes=t.oc)), State.oc),
                                 tasks))
    filtered_tasks.sort(key=lambda t: max(t.oc_start, control.next_freeTime))
    if len(filtered_tasks) == 0:
        return None
        # raise Exception
    # Order by starttime
    return filtered_tasks[0]


def choose_best_meca_task(tasks, mecanic):
    # Task that can be done
    filtered_tasks = list(filter(lambda t: t.block.module.can_work(
        end_date_calc(max(t.meca_start, mecanic.next_freeTime), datetime.timedelta(minutes=Task.kitting)),
        end_date_calc(
            max(t.meca_start, mecanic.next_freeTime),
            datetime.timedelta(minutes=t.meca + Task.kitting)), State.meca), tasks))
    filtered_tasks.sort(key=lambda t: max(t.meca_start, mecanic.next_freeTime))
    if len(filtered_tasks) == 0:
        return None
        # raise Exception
    # Order by starttime
    return filtered_tasks[0]


def addTask2bloc(time, req_mat, req, ms1, ms2, ms3, ms4, fov, gtw):
    tasks = []
    for index, row in time.iterrows():
        t = Task(index, time.loc[index, 'Tps_total'], time.loc[index, 'Tps_QC'])
        t.min_start = req_mat.loc[index, 'Max_livraion']
        tasks.append(t)
        if ms1.name in t.name:
            ms1.addTask(t)
        elif ms2.name in t.name:
            ms2.addTask(t)
        elif ms3.name in t.name:
            ms3.addTask(t)
        elif ms4.name in t.name:
            ms4.addTask(t)
        elif fov.name in t.name:
            fov.addTask(t)
        elif gtw.name in t.name:
            gtw.addTask(t)
        else:
            raise ValueError
    for index, row in req.iterrows():
        t = list(filter(lambda t: t.name == index, tasks))[0]
        if req.loc[index, 'tasks_req'] is not None:
            t.previous = list(filter(lambda t: t.name in req.loc[index, 'tasks_req'], tasks))
            t.pending_prec = len(t.previous)
        if req.loc[index, 'next'] is not None:
            t.next = list(filter(lambda t: t.name in req.loc[index, 'next'], tasks))

def convert_solution_to_df(solution):
    df = pd.DataFrame(index = np.arange(0, (len(solution) * 3)), columns=['Task', 'Start', 'Finish', 'Part', 'IsPresent'])
    for i in range(0, len(solution)):
        df.iloc[3 * i] = [solution[i].name,
                         str(solution[i].kitting_start.date()) + " " + str(solution[i].kitting_start.time()),
                         str(solution[i].kitting_end.date()) + " " + str(solution[i].kitting_end.time()),
                          'kitting',
                          True]
        df.iloc[3 * i + 1] = [solution[i].name,
                             str(solution[i].meca_start.date()) + " " + str(solution[i].meca_start.time()),
                             str(solution[i].meca_end.date()) + " " + str(solution[i].meca_end.time()),
                              'meca',
                              True]
        df.iloc[3 * i + 2] = [solution[i].name,
                             str(solution[i].oc_start.date()) + " " + str(solution[i].oc_start.time()),
                             str(solution[i].oc_end.date()) + " " + str(solution[i].oc_end.time()),
                             'qc',
                             True]
    return df
def solve():
    timeOUEST, req_matOUEST, req_taskOUEST = extract_tasks_from_excel(pathOUEST)
    timeEST, req_matEST, req_taskEST = extract_tasks_from_excel(pathEST)
    add_next2req_task(req_taskEST)
    add_next2req_task(req_taskOUEST)

    est = Module("EST")
    ouest = Module("OUEST")

    ms1 = Bloc("MS1")
    ms2 = Bloc("MS2")
    ms3 = Bloc("MS3")
    ms4 = Bloc("MS4")
    fov = Bloc("FOV")
    gtw = Bloc("GTW")
    ouest.addBloc(ms1)
    ouest.addBloc(ms4)
    ouest.addBloc(gtw)
    est.addBloc(ms2)
    est.addBloc(ms3)
    est.addBloc(fov)
    addTask2bloc(timeEST, req_matEST, req_taskEST, ms1, ms2, ms3, ms4, fov, gtw)
    addTask2bloc(timeOUEST, req_matOUEST, req_taskOUEST, ms1, ms2, ms3, ms4, fov, gtw)
    # for t in gtw.tasks:
    #    print(t.name, [a.name for a in t.next], [a.name for a in t.previous], t.pending_prec)
    # get max_date
    max_date = datetime.datetime(year=2018, month=1, day=1)
    for i in ms1.tasks + ms2.tasks + ms3.tasks + ms4.tasks + fov.tasks + gtw.tasks:
        if i.min_start > max_date:
            max_date = i.min_start
    max_date = start1_of_date(max_date)
    est.start = max_date
    ouest.start = max_date

    # Init ressources
    mecanics = [Resource("r1", Rtype.meca), Resource("r2", Rtype.meca), Resource('r3', Rtype.meca)]
    control = Resource("r1", Rtype.oc)
    for operator in mecanics:
        operator.next_freeTime = max_date
    control.next_freeTime = max_date
    #
    #
    # # la liste des tâche à faire
    ready_to_do = [ms1.tasks.pop(0), ms2.tasks.pop(0), ms3.tasks.pop(0), ms4.tasks.pop(0),
                   fov.tasks.pop(0), gtw.tasks.pop(0)]
    for t in ready_to_do:
        t.meca_start = max(max_date, t.min_start)
        t.state = State.meca
    i = 0
    meca_w = 0
    oc_w = 0
    solution = []
    while len(ready_to_do) != 0:
        i = i + 1
        # print(i)
        # Filter meca resource by next_free_time
        mecanics.sort(key=lambda x: x.next_freeTime)
        # Try to find a meca task to do
        task_found = False
        iter = 0
        task = None
        remaining_meca_tasks = list(filter(lambda x: x.state == State.meca, ready_to_do))
        if len(remaining_meca_tasks) > 0:
            # print("remaining_meca_tasks " + str(len(remaining_meca_tasks)))
            while task is None and iter < len(mecanics):
                mecanic = mecanics[iter]
                iter = iter + 1
                task = choose_best_meca_task(remaining_meca_tasks, mecanic)

            # Do meca task found
            if task is not None:
                task.do_meca(mecanic)

            if iter == len(mecanics) and task is None:
                # Todo
                # print("case except")
                for t in remaining_meca_tasks:
                    t.meca_start = t.block.module.best_start(
                        end_date_calc(t.meca_start, datetime.timedelta(minutes=Task.kitting)),
                        datetime.timedelta(minutes=t.meca))

        # Try to find an oc task to do
        remaining_oc_tasks = list(filter(lambda x: x.state == State.oc, ready_to_do))
        if len(remaining_oc_tasks) > 0:
            # print("remaining_oc_tasks " + str(len(remaining_oc_tasks)))
            task = choose_best_oc_task(remaining_oc_tasks, control)
            if task is not None:
                task.do_oc(control)
                # Ajout des prochaines tâche mais attention 1 tâche peuvent avoir plusieurs précédents
                # Dans ce cas ça marche plus
                for t in task.next:
                    if t.pending_prec == 0:
                        t.meca_start = max(task.oc_end, t.min_start)
                        ready_to_do.append(t)
                        t.state = State.meca
                # Remove the task done
                ready_to_do.remove(task)
                solution.append(task)
            else:
                # print("case except oc")
                for t in remaining_oc_tasks:
                    t.oc_start = t.block.module.best_start(t.oc_start, datetime.timedelta(minutes=t.oc))

    for sol in solution:
        print(sol)
    print("makespan: " + str(makespan(solution)))
    print("nb task done : {0}".format(len(solution)))
    # Check
    est.check()
    ouest.check()
    return convert_solution_to_df(solution)


solution = solve()
print(solution)
# Build a solution based on ResourceOrder solution of jobshop
# Solve it
# Display solution
