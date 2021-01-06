import datetime

from enum import Enum

from src.date_converter import end_date_calc

class State(Enum):
    not_started = 0
    finished = 1
    kitting = 2
    meca = 3
    oc = 4
    ended = 5


class Task:
    kitting = 3*60

    def __init__(self, name, meca, oc):
        self.state = State.not_started
        self.name = name
        self.meca = meca
        self.oc = oc
        self.block= None
        self.previous = []
        self.next = []
        self.min_start = None
        self.pending_prec = None
        self.meca_resource = None
        self.oc_ressource = None
        self.meca_start = None
        self.meca_end= None
        self.oc_start = None
        self.oc_end= None

    def has_next(self):
        return self.next is not None and len(self.next) != 0

    def __str__(self):
        description = self.name
        for next in self.next:
            description = description + " => " + str(next) + "\n"
        return description

    def do_meca(self, resource):
        self.meca_start = max(resource.next_freeTime, self.meca_start)
        self.state = State.oc
        endTime = end_date_calc(self.meca_start, datetime.timedelta(minutes = self.meca))
        self.oc_start = endTime
        self.meca_end = endTime
        self.block.module.inc(self.meca_start, endTime)
        self.meca_resource = resource
        resource.next_freeTime = endTime
        #print("meca " +self.name)

    def __str__(self):
        #return self.name
        description = self.name + "\n"
        description = description + "kitt_meca " + str(self.meca_start.date()) +" "+  str(self.meca_start.time())+ " to "+ str(self.meca_end.date()) +" "+  str(self.meca_end.time())+"\n"
        description = description + "oc " + str(self.oc_start.date()) +" "+ str(self.oc_start.time())+" to "+str(self.oc_end.date()) +" "+ str(self.oc_end.time())+"\n"
        description = description + "mecanic "+ str(self.meca_resource.name)
        return description + "\n"

    def do_oc(self, resource):
        self.oc_start = max(resource.next_freeTime, self.oc_start)
        self.state = State.finished
        endTime = end_date_calc(self.oc_start, datetime.timedelta(minutes=self.oc))
        self.oc_end = endTime
        resource.next_freeTime = endTime
        self.block.module.inc(self.oc_start, endTime)
        for t in self.next:
            t.pending_prec = t.pending_prec - 1
        #print("oc " +self.name)