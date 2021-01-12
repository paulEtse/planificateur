from extractor import Extract_data
#from src.solver import SolveurPPC
#from src import date_converter
from datetime import datetime, timedelta
import pandas as pd


#date = datetime(2019,11,1,1,0,0)

#for i in range(50):
#    ts = datetime.timestamp(date)
#    print("Original date : ", date, ts)
#    worktime = date_converter.convert_to_work_time(ts)
#    print("worktime :" , worktime)
#    converted = date_converter.convert_to_timestamp(worktime)
#    print("converted date : ", datetime.fromtimestamp(converted) ,converted )
#    date = date + timedelta(days = 1)

#-------------------------------------------------------------------------------------------

timeOUEST, req_matOUEST, req_taskOUEST = Extract_data.extract_tasks_from_excel(Extract_data.pathOUEST)
timeEST, req_matEST, req_taskEST = Extract_data.extract_tasks_from_excel(Extract_data.pathEST)

def check_nouvelle_livraison(jour, mois, annee, etiq_product, last_solution=[], model=[]):
    need_solve_again = True

    date = datetime(annee,mois,jour)
    date_timestamp = datetime.timestamp(date)
    #date_work_time = date_converter.convert_to_work_time(date_timestamp)

    #dates des livraisons
    livraisons = (pd.read_excel("./data/livraison guides.xlsx",parse_dates=['livraison au MAG AIT'])).iloc[:,2:]

    #---------------- recherche date originale ----------------
    found = False
    size = len(livraisons["Etiquettes TOPO"])
    for i in range(size):
        l = livraisons["Etiquettes TOPO"][i]
    
        if (l == etiq_product):
            found = True
            date_origin = livraisons["livraison au MAG AIT"][i]
            #print(type(date_origin))
            #<class 'pandas._libs.tslibs.timestamps.Timestamp'>
            #<=> datetime !!

            # maj date livraison ==============================================================================

    #---------------- vérification écart date ----------------
    plus_tot = False
    plus_tard = False

    if not(found):
        print("problème - référence pas trouvée")
        need_solve_again = False
        #len(livraisons) == 0 ???
    else:
        livraison_before_origin = date < date_origin
        livraison_equals_origin = (date == date_origin)
        if (livraison_equals_origin): 
            print("date livraison non changée")
            need_solve_again = False
        elif(livraison_before_origin):
            print("date livraison plut tôt que prévu")
            plus_tot = True
        else:
            print("date livraison plut tard que prévu")
            plus_tard = True
    
    #---------------- recherche tâches + min dates tâches ----------------
    found_tasks_EST = False
    num_EST = 0
    tasks_EST_i = []
    tasks_EST = []
    dates_min_EST = []

    found_tasks_OUEST = False
    num_OUEST = 0
    tasks_OUEST_i = []
    tasks_OUEST = []
    dates_min_OUEST = []

    if need_solve_again:
        print("---------------- recherche tâches + min dates tâches ----------------")

        #---------------- recherche EST
        for i in range(len(req_matEST)):
            task = req_matEST.index[i]
            liste_produits_livraison = req_matEST.iloc[i,0]
            min_start_date = req_matEST.iloc[i,2]
            #min_start_time = datetime.timestamp(pd.to_datetime(min_start_date))

            if etiq_product in liste_produits_livraison:
                print("ok EST : task = ", task)
                found_tasks_EST = True
                tasks_EST_i.append(i)
                tasks_EST.append(task)
                dates_min_EST.append(min_start_date)

        #---------------- recherche OUEST
        for i in range(len(req_matOUEST)):
            task = req_matOUEST.index[i]
            liste_produits_livraison = req_matOUEST.iloc[i,0]
            min_start_date = req_matOUEST.iloc[i,2]
            #min_start_time = datetime.timestamp(pd.to_datetime(min_start_date))

            if etiq_product in liste_produits_livraison:
                print("ok OUEST : task = ", task)
                found_tasks_OUEST = True
                tasks_OUEST_i.append(i)
                tasks_OUEST.append(task)
                dates_min_OUEST.append(min_start_date)

        num_EST = len(tasks_EST_i)
        num_OUEST = len(tasks_OUEST_i)

        found_tasks = found_tasks_EST or found_tasks_OUEST
        if (not found_tasks):
            print("problème - aucune tâche trouvée pour la référence")
            need_solve_again = False
    
    #---------------- vérification min dates ----------------
    #si plus tard 
    #toutes les taches ont un min superieur a date => rien a faire
    #une des taches a un min inferieur a date => min de cette tache a maj + solve again
    if need_solve_again and plus_tard:
        print("---------------- vérification min dates ----------------\n si plus tard")

        #recherche un min de tache < date
        found_min_inf = False

        if found_tasks_EST:
            for i in range(num_EST):
                current_date = dates_min_EST[i]
                if current_date < date:
                    #maj min (:= date) de la tache d'index tasks_EST_i[i] et de nom tasks_EST[i] ======================
                    found_min_inf = True
    
        if found_tasks_OUEST:
            for i in range(num_OUEST):
                current_date = dates_min_OUEST[i]
                if current_date < date:
                    #maj min (:= date) de la tache d'index tasks_OUEST_i[i] et de nom tasks_OUEST[i] ==================
                    found_min_inf = True
        
        if (not found_min_inf):
            print("tâches trouvées pour la référence : déjà une date min supérieure")
            need_solve_again = False
    
    #si plus tot
    #toutes les taches ont un min superieur a origin => rien a faire
    #une des taches a un min egal a origin  => recalcul du min de cette tache avec autre produits : si une amélioration => solve again
    if need_solve_again and plus_tot:
        print("---------------- vérification min dates ----------------\n si plus tot")

        #recherche un min de tache == date_origin améliorant !
        found_min_mieux = False

        if found_tasks_EST:
            for i in range(num_EST):
                current_task = tasks_EST[i]
                current_num_task = tasks_EST_i[i]
                current_date = dates_min_EST[i]
                liste_produits_current_task = req_matEST.iloc[current_num_task,0]

                if current_date == date_origin:
                    
                    #recalcul : est-ce que date_origin dependait uniquement du produit changé ?
                    max_livraison = date
                    for ref,date_liv in livraisons.iloc[:].values:
                        if ref in liste_produits_current_task:
                            if date_liv > max_livraison:
                                max_livraison = date_liv

                    if max_livraison < date_origin:
                        #maj min (:= max_livraison) de la tache d'index current_num_task et de nom current_task ======================
                        found_min_mieux = True
    
        if found_tasks_OUEST:
            for i in range(num_OUEST):
                current_task = tasks_OUEST[i]
                current_num_task = tasks_OUEST_i[i]
                current_date = dates_min_OUEST[i]
                liste_produits_current_task = req_matOUEST.iloc[current_num_task,0]

                if current_date == date_origin:
                    
                    #recalcul : est-ce que date_origin dependait uniquement du produit changé ?
                    max_livraison = date
                    for ref,date_liv in livraisons.iloc[:].values:
                        if ref in liste_produits_current_task:
                            if date_liv > max_livraison:
                                max_livraison = date_liv

                    if max_livraison < date_origin:
                        #maj min (:= max_livraison) de la tache d'index current_num_task et de nom current_task ======================
                        found_min_mieux = True
        
        if (not found_min_mieux):
            print("tâches trouvées pour la référence : toutes avec un autre produit de date min supérieure")
            need_solve_again = False

    return need_solve_again

#test tache ouest - plus tard
check_nouvelle_livraison(2, 4, 2019, "W10111C", last_solution=[], model=[])