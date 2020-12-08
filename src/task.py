from enum import Enum


class State(Enum):
    not_started = 0
    finished = 1
    kitting = 2
    meca = 3
    oc = 4
    ended = 5


class Task:
    kitting = 3

    def __init__(self, name, bloc, meca, oc):
        self.state = State.not_started
        self.name = name
        self.bloc = bloc
        self.meca = meca
        self.oc = oc
        self.previous = []
        self.next = []
        self.min_start = None
        self.pending_prec = None

    def has_next(self):
        return self.next is not None and len(self.next) != 0

    def __str__(self):
        description = self.name
        for next in self.next:
            description = description + " => " + str(next) + "\n"
        return description