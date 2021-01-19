from extractor import Extract_data
from src.solver.SolveurPPC import SolveurPPC


ppc = SolveurPPC()
#ppc.print_OUEST()
#ppc.print_EST()

#ppc.create_model(0,30*60, "Restart", 1)
ppc.create_model(0,10*60*60, "Restart", 1)
#ppc.create_model(2,60*60, "DepthFirst")
#ppc.create_model(2,60*60, "MultiPoint")
# ppc.create_model(5,60*60)
# ppc.create_model(10,60*60)

