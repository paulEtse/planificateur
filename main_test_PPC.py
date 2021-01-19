from extractor import Extract_data
from src.solver.SolveurPPC import SolveurPPC


ppc = SolveurPPC()
# ppc.print_OUEST()
# ppc.print_EST()

# ppc.create_model(0,30*60, "Restart", 1)
#ppc.main( True, 60, "")
#ppc.main(False,60,"Solution_PPC_60_sec_7_type_Restart.json")
# ppc.create_model(2,60*60, "DepthFirst")
# ppc.create_model(2,60*60, "MultiPoint")
# ppc.create_model(5,60*60)
# ppc.create_model(10,60*60)
ppc.add_constraint("Solution_PPC_60_sec_7_type_Restart.json")
