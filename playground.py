#notes:
#set data rate at 0.2 Hz

#input
#k = input("Enter case number (##):")

#initiliaze arrays to be used for Pandas
time_MT, time_FT_1, time_BT = [],[],[]
data_AF, data_AP, data_KM = [],[],[]
data_UO, data_sO2v, data_hct = [],[],[]

#necessary libraries
import serial as ser
import threading
import numpy as np
import time
import pandas as pd
import matplotlib as plt

#integrating multiple ports at once, threading
#initialize
MT = ser.Serial("COM3", 9600, timeout=1000)
FT_1 = ser.Serial("COM4", 2400, timeout=1000)
#FT_2 = ser.Serial("COM5", 2400, timeout=1000)
#BT = ser.Serial("COM6", 9600, timeout=1000)
MT.write(b'DR 05 013B\r')

#threading functions
#arterial flow and pressure
def MT_port(s):
    while True:
        global time_MT
        end_MT = time.ctime()
        time_MT.append(end_MT)
        MT_byte = s.read(35)
        MT_str = str(MT_byte)
        AF_str = MT_str[5:8] + "." + MT_str[8:10]
        AP_str = MT_str[11:15]
        global data_AF, data_AP

        if MT_str[5] == "+" and MT_str[11] == "+":
            data_AF.append(float(AF_str[1:5]))
            data_AP.append(float(AP_str[12:15]))
        elif MT_str[5] == "+" and MT_str[11] == "+":
            data_AF.append(float(AF_str[1:5]))
            data_AP.append(float(AP_str[11:15]))
        elif MT_str[5] != "+" and MT_str[11] == "+":
            data_AF.append(float(AF_str[0:5]))
            data_AP.append(float(AP_str[12:15]))
        else:
            data_AF.append(float(AF_str[0:5]))
            data_AP.append(float(AP_str))
        print(f"{AF_str} {AP_str} {end_MT}")

#kidney mass            
def FT_1_port(s):
    i = 0
    j = 39
    while True:
        global time_FT_1
        end_FT_1 = time.ctime()
        time_FT_1.append(end_FT_1)
        FT_1_byte = s.read(16)
        FT_1_str = str(FT_1_byte)
        global data_KM
        if (lap_FT_1%5 == 0 and lap_FT_1 != 0) and FT_1_str[4] == ".":
            if i == j:
                j += 75
                pass
            else:
                data_KM.append(float(FT_1_str[2:8]))
                print(f"{FT_1_str[2:8]} {end_FT_1}")
        i += 1

#urine output/mass            
def FT_2_port(s):    
    i = 0
    j = 39
    while True:
        end_FT_2 = time.time()
        lap_FT_2 = round(end_FT_2 - init)
        FT_2_byte = s.read(16)
        FT_2_str = str(FT_2_byte)
        global data_UO
        if (lap_FT_2%5 == 0 and lap_FT_2 != 0) and FT_2_str[4] == ".":
            if i == j:
                j += 75
                pass
            else:
                data_UO.append(float(FT_2_str[2:8]))
                print(f"{FT_2_str[2:8]} {lap_FT_2-5}")
        i += 1        
        
#sO2 and hct
def BT_port(s):
    while True:
        global time_BT
        end_BT = time.ctime()
        time_BT.append(end_BT)
        BT_byte = s.read(43)
        BT_str = str(BT_byte)
        global data_sO2v, data_hct
        data_sO2v.append(BT_str[2:14])
        data_hct.append(BT_str[15:22])
        print(f"{FT_1_str[2:22]} {end_BT}")
    
MT_thread = threading.Thread(target=MT_port, args=(MT),)
FT_1_thread = threading.Thread(target=FT_1_port, args=(FT_1),)
#FT_2_thread = threading.Thread(target=FT_2_port, args=(FT_2,start),)
#BT_thread = threading.Thread(target=BT_port, args=(BT),)

MT_thread.start()
FT_1_thread.start()
#FT_2_thread.start()
#BT_thread.start()

MT_thread.join()
FT_1_thread.join()
#FT_2_thread.join()
#BT_thread.join()

#creating dataframe for kidney data
comb = {"MedTronic Date/Time": time_MT, "Arterial Flow (L/min)": data_AF, 
        "Arterial Pressure (mmHg)": data_AP,"Force Transducer Date/Time": time_FT_1, "Kidney Mass (kg)": data_KM}
BT_set = {"BioTrend Date/Time": time_BT, "sO2 Venous": data_sO2v, "Hematocrit": data_hct}

#"Urine Output (kg)": data_UO, "O2 Sat (Venous)": data_sO2v, "Hematocrit": data_hct
data_matrix = pd.DataFrame(comb)
BT_df = pd.DataFrame(BT_set)
print(data_matrix)
print(BT_df)
data_matrix.to_csv("data_test.csv",index=False)

MT.close()
FT_1.close()
#FT_2.close()
#BT_.close
