from extractor import Extract_data
from src.solver.SolveurPPC import SolveurPPC


ppc = SolveurPPC()
#ppc.print_OUEST()
#ppc.print_EST()
for i in range(25):
    ppc.create_model(i,500)