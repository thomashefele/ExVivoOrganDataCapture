import serial as ser
import time

s = ser.Serial("COM4", 2400, timeout=1000)
data_KM = []
time_FT_1 = []

start = time.time()

i = 1
Sum = 0
while True:
    global time_FT_1
    end_FT_1 = time.ctime()
    lap_FT_1 = round(time.time() - start)
    time_FT_1.append(end_FT_1)
    FT_1_byte = s.read(6)
    FT_1_str = str(FT_1_byte)
    if lap_FT_1%5 == 0:
        avg = Sum/i
        print(f"{avg} {end_FT_1}")
        Sum = 0
        i = 1
    else:
        Sum += float(FT_1_str[2:8])
        i += 1
    global data_KM
    data_KM.append(FT_1_str)
    
    #------------------------------------------------------------------------------
    
    #necessary libraries
import serial as ser
import threading
import numpy as np
import time
import pandas as pd
import matplotlib as plt

MT = ser.Serial("COM3", 9600, timeout=1000)
MT.write(b'DR 05 013B\r')
time_MT = []
data_AF = []
data_AP = []

while True:
    global time_MT
    end_MT = time.ctime()
    time_MT.append(end_MT)
    MT_byte = MT.read(35)
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
    
    #-----------------------------------------------------------------------------
    
import serial as ser
import time

s = ser.Serial("COM6", 9600, timeout=1000)

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
