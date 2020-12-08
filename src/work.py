from src.task import State, Task
from src.holidays import end_date_calc
import datetime

class Work:
    def __init__(self, task):
        # self.kit_resource = []
        self.meca_resource = None
        self.oc_ressource = None
        self.task = task
        self.meca_start = None
        self.oc_start = None
        # self.kitting_start = None
    def get_meca_start(self):
        return self.meca_start

    # def do_kitting(self, resources):
    # todo

    def do_meca(self, resource):
        self.meca_start = max(resource.next_freeTime, self.meca_start)
        self.task.state = State.oc
        endTime = end_date_calc(self.meca_start, datetime.timedelta(hours = (Task.kitting + self.task.meca)))
        self.oc_start = endTime
        self.task.state = State.meca
        self.meca_resource = resource
        resource.next_freeTime = endTime
    def __str__(self):
        description = self.task.name + "\n"
        description = description + "kitt_meca " + str(self.meca_start.date()) +" "+  str(self.meca_start.time())+"\n"
        description = description + "oc " + str(self.oc_start.date()) +" "+ str(self.oc_start.time())+"\n"
        description = description + "mecanic "+ str(self.meca_resource.name)
        return description + "\n"

    def do_oc(self, resource):
        self.oc_start = max(resource.next_freeTime, self.oc_start)
        self.task.state = State.finished
        resource.next_freeTime = end_date_calc(self.oc_start, datetime.timedelta(hours=self.task.oc))
        for t in self.task.next:
            t.pending_prec = t.pending_prec - 1

    def get_state_at(self, date):
        if date < self.meca_start:
            return None
        elif date < (self.meca_start + self.task.meca + self.task.kitting):
            return State.meca
        elif date < (self.oc_start + self.task.oc):
            return State.oc
        else:
            return None
