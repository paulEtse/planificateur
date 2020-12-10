
from extractor import Extract_data

timeOUEST, req_matOUEST, req_taskOUEST = Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
print(timeOUEST, req_matOUEST, req_taskOUEST )