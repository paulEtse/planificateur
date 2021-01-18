from dateutil import parser
from datetime import datetime
import requests

from src.solver.SolveurPPC import SolveurPPC

#time.sleep(40) #Security

baseUrl = 'https://qrfx7lea3b.execute-api.eu-west-3.amazonaws.com/dev'

r = requests.get(baseUrl + '/project/parameters')
data = r.json()
changes = r.status_code < 400

while changes:
    startAt = datetime.now()
    ppc = SolveurPPC()
    ppc.create_model(data['METHOD'], 60*data['DURATION'])

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

#os.system('sudo shutdown now -h')