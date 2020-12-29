import numpy as np
import datetime
from src.holidays_m import isHolliday


class Module:
    def __init__(self, name):
        self.name = name
        self.blocs = []
        self.start = None
        self.nb_op = np.zeros(shape=90 * 24 * 60)

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

    def can_work(self, start_ , to):
        answer = True
        start_index = int((start_ - self.start).total_seconds() / 60)
        end_index = int((to - self.start).total_seconds() / 60)
        i = start_index
        while(i <= end_index and self.nb_op[i] < 2):
            i=i+1
        return answer

    def best_start(self, start_):
        index = int((start_ - self.start).total_seconds() / 60)
        i = index
        while self.nb_op[i] >= 2 or isHolliday(self.start + datetime.timedelta(minutes= i)):
            i = i + 1
        return self.start + datetime.timedelta(minutes=i)