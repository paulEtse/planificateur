from src.solver import BasicSolver
from src.resource import Resource, rType
from src.module import Module
from src.bloc import Bloc

#Build a first version of solution
#Use integer instead of dates (start = 0)
#Assume that time is continuous (no stop, no weekend, ...)
#Unit of time minute
#Use only ten 10 first tasks of each block
#Assume that we have 3 meca ressources and 1 oc

r = [Resource("r1", rType.oc), Resource("r2", rType.meca), Resource("r3", rType.meca), Resource('r4', rType.meca)]
#Solve it

#Display solution