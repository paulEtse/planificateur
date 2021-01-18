import numpy as np
import datetime
from src.task import Task, State
from src.date_converter import end_date_calc, end2_of_date


class Module:
    def __init__(self, name):
        self.name = name
        self.blocs = []
        self.start = None
        self.nb_op = np.zeros(shape=120 * 24 * 60)

    def addBloc(self, bloc):
        self.blocs.append(bloc)
        bloc.module = self

    def inc(self, start_, to):
        start = int((start_ - self.start).total_seconds() / 60)
        end = int((to - self.start).total_seconds() / 60)
        self.nb_op[start:end] = self.nb_op[start:end] + 1

    def get_nb_op_status(self, start_):
        index = int((start_ - self.start).total_seconds() / 60)
        return self.nb_op[index]

    def can_work(self, start_ , to, state):
        #if state == State.meca and end_date_calc(start_, datetime.timedelta(minutes=Task.kitting)) > end2_of_date(start_):
            # print("###### {0}".format(start_))
        #    return False
        start_index = int((start_ - self.start).total_seconds() / 60)
        end_index = int((to - self.start).total_seconds() / 60)
        i = start_index
        while i <= end_index and self.nb_op[i] < 2:
            i=i+1
        return self.nb_op[i] < 2

    def best_start(self, start_, duration):
        start = start_
        index_1 = int((start - self.start).total_seconds() / 60)
        end = end_date_calc(start, duration=duration)
        index_2 = int((end - self.start).total_seconds() / 60)
        i = index_1
        while i < index_2:
            if self.nb_op[i] == 2:
                start = self.start + datetime.timedelta(minutes=i)
                end = end_date_calc(start, duration=duration)
                #index_1 = int((start - self.start).total_seconds() / 60)
                index_2 = int((end - self.start).total_seconds() / 60)
            i=i+1
        return start

    def check(self):
        for i in self.nb_op:
            assert (i <= 2)