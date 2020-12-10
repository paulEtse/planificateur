import numpy as np
import minilp
import pandas as pd
from pathlib import Path
import math


pathOUEST = Path("./data/Sequencement OUEST Modified.xlsx")
pathEST = Path("./data/Sequencement EST Modified.xlsx")


def extract_tasks_from_excel(path):
    livraisons = (pd.read_excel("./data/livraison guides.xlsx",parse_dates=['livraison au MAG AIT'])).iloc[:,2:]
    #print(livraisons)
    xlsx = pd.read_excel(path,sheet_name=None)
    time = pd.DataFrame(index = list(xlsx.keys()),columns=["Tps_pieds","Tps_guides","Tps_total","Tps_QC"])
    req_mat = pd.DataFrame(index = list(xlsx.keys()),columns=["Livraison","Stock","Max_livraion"])
    req_task = pd.DataFrame(index = list(xlsx.keys()),columns=["tasks_req"])
    for task in xlsx : 
        for index,value in enumerate(xlsx[task].iloc[:,8]):
            if value == "Tps pieds":
                pieds = xlsx[task].iloc[index+1,8]
            if value == "Tps guides":
                guides = xlsx[task].iloc[index+1,8]
            if value == "Tps total":
                total = xlsx[task].iloc[index+1,8]
            if value == "Tps QC":
                QC = xlsx[task].iloc[index+1,8]
        time.loc[task,"Tps_pieds"] = pieds
        time.loc[task,"Tps_guides"] = guides
        time.loc[task,"Tps_total"] = total
        time.loc[task,"Tps_QC"] = QC
        req_mat_list = xlsx[task].iloc[:,0].dropna()
        livraison = []
        stock = []
        for ref in np.asarray(req_mat_list):
            if ref[0] =='W':
                livraison.append(ref)
            else:
                stock.append(ref)
        max_livraion = livraisons.iloc[0,1]
        if(len(livraison)>0):
            #print(livraisons.iloc[2:].values)
            for ref,date in livraisons.iloc[:].values:
                if ref in livraison:
                    if date > max_livraion:
                        max_livraion = date        
        req_mat.loc[task,"Max_livraion"] = max_livraion      
        req_mat.loc[task,"Livraison"] = list(livraison)
        req_mat.loc[task,"Stock"] = list(stock)

        i = 0
        req = []
        # print(xlsx[task].iloc[:,1])
        while(not pd.isna(xlsx[task].iloc[i,1])):
            #print(xlsx[task].iloc[i,1])
            req.append(xlsx[task].iloc[i,1])
            i+=1
        req_task.loc[task,"tasks_req"] = list(req)


    return(time,req_mat,req_task)