from enum import Enum
class rType(Enum):
    meca = 0
    oc = 1

class Resource:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.next_freeTime = 0
