#notes:
#set data rate at 0.2 Hz

#input
k = input("Enter case number (##):")

#initiliaze arrays to be used for Pandas
data_AF, data_AP, data_KM, data_UO, data_sO2v, data_hct = [],[],[],[],[],[]

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
FT_2 = ser.Serial("COM5", 2400, timeout=1000)
BT = ser.Serial("COM6", 9600, timeout=1000)
start = time.time()
MT.write(b'DR 051 013B\r')

#threading functions
#arterial flow and pressure
def MT_port(s,init):
    while True:
        end_MT = time.time()
        lap_MT = round(end_MT - init)
        MT_byte = s.read(35)
        MT_str = str(MT_byte)
        global data_AF, data_AP
        
        match MT_str[5], MT_str[11]:
            case "+","+":
                data_AF.append(float(MT_str[6:10]))
                data_AP.append(float(MT_str[6:10]))
            case "+","-":
                data_AF.append(float(MT_str[6:10]))
                data_AP.append(float(MT_str[5:10]))
            case "+","-":
                data_AF.append(float(MT_str[5:10]))
                data_AP.append(float(MT_str[6:10]))
            case _:
                data_AF.append(float(MT_str[5:10]))
                data_AP.append(float(MT_str[5:10]))
        print(f"{MT_str[5:15]} {lap_MT}")

#kidney mass            
def FT_1_port(s,init):
    i = 0
    j = 39
    while True:
        end_FT_1 = time.time()
        lap_FT_1 = round(end_FT_1 - init)
        FT_1_byte = s.read(16)
        FT_1_str = str(FT_1_byte)
        global data_KM
        if (lap_FT_1%5 == 0 and lap_FT_1 != 0) and FT_1_str[4] == ".":
            if i == j:
                j += 75
                pass
            else:
                data_KM.append(float(FT_1_str[2:8]))
                print(f"{FT_1_str[2:8]} {lap_FT_1-5}")
        i += 1

#urine output/mass            
def FT_2_port(s,init):    
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
def BT_port(s,init):
#in progress
    
MT_thread = threading.Thread(target=MT_port, args=(MT,start),)
FT_1_thread = threading.Thread(target=FT_1_port, args=(FT_1_,start),)
FT_2_thread = threading.Thread(target=FT_2_port, args=(FT_2,start),)
BT_thread = threading.Thread(target=BT_port, args=(BT,start),)

MT_thread.start()
FT_1_thread.start()
FT_2_thread.start()
BT_thread.start()

#real time data graphing:
#in progress    

MT_thread.join()
FT_1_thread.join()
FT_2_thread.join()
BT_thread.join()

#creating dataframe for kidney data
comb = {"Arterial Flow (L/min)": data_AF, "Arterial Pressure (mmHg)": data_AP, 
        "Kidney Mass (kg)": data_KM, "Urine Output (kg)": data_UO, 
        "O2 Sat (Venous)": data_sO2v, "Hematocrit": data_hct}
data_matrix = pd.DataFrame(comb)
with data_matrix.to_csv("DTK_data.csv",f"case{k}",True)

MT.close()
FT_1.close()
FT_2.close()
BT_.close
