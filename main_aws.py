from dateutil import parser
from datetime import datetime
import requests
import os
import time

import pandas as pd
from src import Solution
from src.solver.SolveurPPC import SolveurPPC

from docplex.cp.config import context
# context.solver.agent = 'local'
# context.solver.local.execfile = '/opt/ibm/ILOG/CPLEX_Studio201/cpoptimizer/bin/x86-64_linux/cpoptimizer'

shutdown = False
if shutdown:
	time.sleep(40) #Security

baseUrl = 'https://qrfx7lea3b.execute-api.eu-west-3.amazonaws.com/dev'

r = requests.get(baseUrl + '/project/parameters')
data = r.json()
changes = r.status_code < 400

while changes:
    r = requests.get(baseUrl + '/project/solution?gantt=0')
    if r.status_code >= 400:
        break

    startAt = datetime.now()
    ppc = SolveurPPC()
    #print(r.json())
    starting_solution = Solution.generate_Solution_from_json(r.json())
    solution = ppc.add_constraint(starting_solution, 10*data['DURATION']) #TO CHANGE
    print(solution)

    #r = requests.post(baseUrl + '/project/solution', json=solution.to_json())

    r = requests.get(baseUrl + '/project/parameters')
    data = r.json()
    if r.status_code >= 400:
        break
    if parser.isoparse(data['modifiedAt']) > startAt:
        continue

    r = requests.get(baseUrl + '/project/constraints')
    if r.status_code >= 400:
        break
    for constraint in reversed(r.json()):
        if parser.isoparse(constraint['modifiedAt']) > startAt:
            continue

    changes = False

if shutdown:
	os.system('sudo shutdown now -h')
