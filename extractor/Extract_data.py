import numpy as np
import minilp
import pandas as pd


livraisons_xlsx = pd.read_excel("./data/livraison guides.xlsx",parse_dates=['livraison au MAG AIT'])



path = "./data/Sequencement EST Modified.xlsx"


def extract_tasks_from_excel(path):
    xlsx = pd.read_excel(path,sheet_name=None)
    time = pd.DataFrame(index = list(xlsx.keys()),columns=["Tps_pieds","Tps_guides","Tps_total"])
    requirements = pd.DataFrame(index = list(xlsx.keys()),columns=["Livraison","Stock","Max_livraion"])
    for task in xlsx : 
        for index,value in enumerate(xlsx[task].iloc[:,8]):
            if value == "Tps pieds":
                pieds = xlsx[task].iloc[index+1,8]
            if value == "Tps guides":
                guides = xlsx[task].iloc[index+1,8]
            if value == "Tps total":
                total = xlsx[task].iloc[index+1,8]
                
        time.loc[task,"Tps_pieds"] = pieds
        time.loc[task,"Tps_guides"] = guides
        time.loc[task,"Tps_total"] = total
        requirements = np.asarray(xlsx[task].iloc[:,0].dropna())
        livraison = []
        stock = []
        for ref in requirements:
            if ref[0] =='W':
                livraison.append(ref)
            else:
                stock.append(ref)
        max_livraion = livraisons.iloc[0,1]
        if(len(livraison)>0):
            #print(livraisons.iloc[:].values)
            for ref,date in livraisons.iloc[:].values:
                if ref in livraison:
                    if date > max_livraion:
                        max_livraion = date
        requirements.loc[task,"Max_livraion"] = max_livraion      
        requirements.loc[task,"Livraison"] = list(livraison)
        requirements.loc[task,"Stock"] = list(stock)
    return(time,requirements)
extract_tasks_from_excel(path)