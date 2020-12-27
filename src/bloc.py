import numpy as np
class Bloc:
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.module = None
    def addTask(self, task):
        self.tasks.append(task)
        task.block = self
    def __str__(self):
        description = self.name +" " + str(len(self.tasks))+ "\n"
        for t in self.tasks:
            description = description + t.name+ " "
        return description + "\n"
    def total_mec(self):
        return np.sum(np.array([x.meca for x in self.tasks]))