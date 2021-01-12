from extractor import Extract_data
from src.solver.SolveurPPC import SolveurPPC


ppc = SolveurPPC()
#ppc.print_OUEST()
#ppc.print_EST()
ppc.create_model(1,60*60)
ppc.create_model(5,60*60)
ppc.create_model(10,60*60)