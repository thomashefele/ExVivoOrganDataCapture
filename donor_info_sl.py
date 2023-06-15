import numpy as np, pandas as pd
import os, sys, platform, csv
from time import monotonic, sleep
from datetime import datetime, timedelta
from pandastable import Table

no_fitz = False

try:
    import fitz
    print("PyMuPDF installed")
except ImportError:
    no_fitz = True
    print("PyMuPDF not installed")

unos_ID = input("Enter UNOS ID: ")

#This function acts as a CSV file writer that serves as a backup for the SQL database in the case that a connectivity error (unsuitable driver,
#no firewall access, no internet connection, etc.) arises during the perfusion so that no data is lost.
def file_write(file_name, h_array, r_array):
    h = False

    try:
        with open(file_name, "r") as file:
            r = csv.reader(file)
            h_row = next(r)

            if h_row == h_array:
                h = True

    except FileNotFoundError:
        pass

    with open(file_name, "a") as file:
        a = csv.writer(file)

        if h == False:
            a.writerow(h_array)

        a.writerow(r_array)

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)             
        else:
            pass

def position_tracker(arr, length, idx= None):
    pos = []

    for i in range(length):
        pos_p = []

        if idx != None:
            for j in range(lt):
                if txt_arr[j].find(arr[i][idx]) != -1:
                    pos_p.append(j) 

            pos.append(pos_p)
        else:
            for j in range(lt):
                if txt_arr[j].find(arr[i]) != -1:
                    pos.append(j)
    return pos

def donor_upload(data):
    don_row = [None]*58
    upload_status, file_status = True, True

    try:
        df = data.transpose()

        head_row = ["blood_type","UNOS_ID","match_ID","height","weight","age","bmi","gender","kdpi","eth_race","cause",
                    "mech","circ","cold_time","dcd","card_ar","CPR","diabetes","cancer","hypert","CAD","GI_dis","smoker","etoh",            
                    "iv_drug","BP_avg","HR_avg","BP_high","dur_high","BP_low","dur_low","wbc","rbc","hgb","hct","plt","Na","K","Cl",            
                    "BUN","crea","glu","tbili","dbili","idbili","sgot","sgpt","aphos","prothr","ptt","l_biop","l_glom_per","l_type",            
                    "l_glom","r_biop","r_glom_per","r_type","r_glom"]

        don_row = [df.iloc[1,0],df.iloc[1,1],df.iloc[1,2],df.iloc[1,3],df.iloc[1,4],df.iloc[1,5],df.iloc[1,6],
                   df.iloc[1,7],df.iloc[1,8],df.iloc[1,9],df.iloc[1,10],df.iloc[1,11],df.iloc[1,12],df.iloc[1,13],
                   df.iloc[1,14],df.iloc[1,15],df.iloc[1,16],df.iloc[1,17],df.iloc[1,18],df.iloc[1,19],
                   df.iloc[1,20],df.iloc[1,21],df.iloc[1,22],df.iloc[1,23],df.iloc[1,24],df.iloc[1,25],
                   df.iloc[1,26],df.iloc[1,27],df.iloc[1,28],df.iloc[1,29],df.iloc[1,30],df.iloc[1,31],
                   df.iloc[1,32],df.iloc[1,33],df.iloc[1,34],df.iloc[1,35],df.iloc[1,36],df.iloc[1,37],
                   df.iloc[1,38],df.iloc[1,39],df.iloc[1,40],df.iloc[1,41],df.iloc[1,42],df.iloc[1,43],
                   df.iloc[1,44],df.iloc[1,45],df.iloc[1,46],df.iloc[1,47],df.iloc[1,48],df.iloc[1,49],
                   df.iloc[1,50],df.iloc[1,51],df.iloc[1,52],df.iloc[1,53],df.iloc[1,54],df.iloc[1,55],
                   df.iloc[1,56],df.iloc[1,57]] 

        for i in range(0,58):
            if isinstance(don_row[i], float):
                if np.isnan(don_row[i]):
                    don_row[i] = None
                    
    except (KeyError, IndexError, pd.errors.InvalidIndexError):
        pass

    try:
        file_write("{}_donor_info.csv".format(unos_ID), head_row, don_row)
        print("File save successful")
    except (PermissionError, OSError, IOError):
        file_status = False
        print("Unable to save to file.")

if no_fitz == False:
    donor_file = find("{}.pdf".format(unos_ID), "/")
    doc = fitz.open(donor_file)
    text = ""
    txt_arr = []

    for page in doc: 
        text = page.get_text()
        temp = text.split("\n")
        temp = temp[4:]

        for i in temp:
            if i == " ":
                pass
            else:
                txt_arr.append(i)

    param = [['Blood Type:','Donor Summary for ***** *****'], ['Donor ID: ','Printed on:'], ['Height: ','Date of birth: '], 
               ['Weight: ','Age: '], ['Age: ','Body Mass Index (BMI): '], ['Body Mass Index (BMI): ','Gender: '],
               ['Gender: ','KDPI:'], ['KDPI:','Ethnicity/race: '], ['Ethnicity/race: ', 'Cause of death: '],
               ['Cause of death: ','Mechanism of injury: '], ['Mechanism of injury: ','Circumstance of death: '],
               ['Circumstance of death: ', 'Admit date:'], ['Cold Ischemic Time:','OR Date:'],
               ['Donor meets DCD criteria: ','Cardiac arrest/downtime?: '], ['Cardiac arrest/downtime?: ','CPR administered?: '], 
               ['CPR administered?: ','Donor Highlights: '],['History of diabetes: ','History of cancer: '],
               ['History of cancer: ','History of hypertension: '], ['History of hypertension: ','History of coronary artery disease (CAD): '],          
               ['History of coronary artery disease (CAD): ','Previous gastrointestinal disease: '],
               ['Previous gastrointestinal disease: ', 'Chest trauma: '], 
               ['Cigarette use (>20 pack years) ever: ','Heavy alcohol use (2+ drinks/daily): '],
               ['Heavy alcohol use (2+ drinks/daily): ','I.V. drug usage: '],
               ['I.V. drug usage: ','According to the OPTN policy in effect on the date of referral'], 
               ['Average/Actual BP','Average heart rate (bpm)'],['Average heart rate (bpm)','High BP'],
               ['High BP','Duration at high (minutes)'],['Duration at high (minutes)','Low BP'], 
               ['Low BP','Duration at low (minutes)'], ['Duration at low (minutes)','Core Body Temp.'], 
               ['WBC (thous/mcL)','RBC (mill/mcL)'],['RBC (mill/mcL)','HgB (g/dL)'],['HgB (g/dL)','Hct (%)'], 
               ['Hct (%)','Plt (thous/mcL)'], ['Plt (thous/mcL)','Bands (%)'], ['Na (mEq/L)','K+ (mmol/L)'],
               ['K+ (mmol/L)','Cl (mmol/L)'], ['Cl (mmol/L)','CO2 (mmol/L)'],['BUN (mg/dL)','Creatinine (mg/dL))'], 
               ['Creatinine (mg/dL))','Glucose (mg/dL)'], ['Glucose (mg/dL)','Total Bilirubin (mg/dL)'],
               ['Total Bilirubin (mg/dL)','Direct Bilirubin (mg/dL)'], ['Direct Bilirubin (mg/dL)','Indirect Bilirubin (mg/dL)'],
               ['Indirect Bilirubin (mg/dL)','SGOT (AST) (u/L)'], ['SGOT (AST) (u/L)','SGPT (ALT) (u/L)',],
               ['SGPT (ALT) (u/L)','Alkaline phosphatase (u/L)'], ['Alkaline phosphatase (u/L)','GGT (u/L)'],
               ['Prothrombin (PT) (seconds)','INR'],['PTT (seconds)','Serum Amylase (u/L)']]

    lr_par = ["Left kidney biopsy:","Right kidney biopsy:"]
    ren_par = ["            % Glomerulosclerosis: ","            Biopsy type: ","            Glomeruli Count: "]

    coords,ren_coord,data,trunc = [],[],[],[]
    lt, lp = len(txt_arr), len(param)
    pos_i, pos_f, pos_lr = position_tracker(param, lp, 0), position_tracker(param, lp, 1), position_tracker(lr_par, 2)

    for i in range(lp):  
        l_coords = len(pos_i[i])

        for j in range(l_coords):
            a2o = [pos_i[i][j], pos_f[i][j]]
            coords.append(a2o)

    for i in coords:
        st, prm_l = None, None
        wonky = ["Donor ID:", "Ethnicity/race: ", "Circumstance of death: ", "Donor meets DCD criteria: ", "Cardiac arrest/downtime?: "]
        boo_1, boo_2 = True, True

        for j in wonky:
            st = txt_arr[i[0]].find(j)

            if st != -1:
                prm_l = len(j)
                boo_1 = False
                break
            else:
                pass

        if boo_1 == False:
            p_data = txt_arr[i[0]]

            if p_data.find(wonky[0]) != -1:
                data.append([p_data,[p_data]])
            else:
                data.append([p_data,[(p_data)[st+prm_l:]]])
        else:
            prm = txt_arr[i[0]]
            p_data = txt_arr[(i[0]+1):i[1]]
            l_pd = len(p_data)

            if l_pd == 0:
                p_data = [""]

            for k in data:
                if prm == k[0]:
                    k[1] += p_data
                    boo_2 = False
                    break

            if boo_2 == True:
                data.append([prm, p_data])

    for i in pos_lr:
        if txt_arr[i+1].find("YES") == -1: 
            data.append([txt_arr[i], ["NO"]])

            for j in ren_par:
                data.append([j, ["NA"]])
        else:
            data.append([txt_arr[i], ["YES"]])

            for j in ren_par:
                J = txt_arr[i:].index(j)
                V = J+1

                if txt_arr[i+V].isnumeric():
                    data.append([j,[txt_arr[i+V]]])
                elif txt_arr[i+V].find(ren_par[1]) != -1:
                    data.append([j,["NA"]])
                elif txt_arr[i+V].find(ren_par[2]) != -1:
                    data.append([j,["NA"]])
                elif txt_arr[i+V].find("Kidney Pump Values:") != -1:
                    data.append([j,["NA"]])

    for i in data:
        if isinstance(i[1], list):
            while i[1].count("") != 0:
                i[1].remove("")

            if len(i[1]) == 0:
                i[1].append("NA")

        if i[1][0].find("Donor ID: ") != -1:
            ids = i[1][0].split(" (")
            for j in ids:
                i_id = j.find(":") + 2
                f_id = j.find(")")
                trunc.append(j[i_id:f_id])
        elif len(i[1]) == 1: 
            trunc.append((i[1])[0])
        else:
            trunc.append(", ".join(i[1]))

    df = pd.DataFrame(columns= [param[i][0] for i in range(0,2)]+["Match ID:"]+[param[i][0] for i in range(2,lp)]+[lr_par[0]]+[ren_par[i] for i in range(3)]+[lr_par[1]]+[ren_par[i] for i in range(3)])
    df_length = len(df)

    try:
        df.loc[df_length] = trunc
        df.index = ["Values"]

    except ValueError:
        print("No file associated with such an ID.\nRestart and enter a valid ID\nor enter values manually.")

    table = df.transpose().reset_index().rename(columns={"index":"Parameters"})
    donor_upload(table)
