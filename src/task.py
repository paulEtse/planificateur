class Task:
    def __init__(self, name, bloc,  meca, oc):
        self.name = name
        self.bloc = bloc
        self.kitting = 3
        self.meca = meca
        self.oc = oc
        self.previous = []
        self.next = []
        self.start = None

    def has_next(self):
        return self.next is not None and len(self.next) != 0