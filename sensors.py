#individual sensor test

import serial as ser
import time
import numpy as np
from threading import Thread

#---------------------------
#MedTronic sensor
        
interval = 10
start = time.time()

with ser.Serial("COM3", 9600, timeout= 1000) as MT_port:
        MT_port.write(b"DR 01 0137\r")
        data_AF, data_AP = [],[]
        AF_avg, AP_avg, ts_MT = [],[],[]

        while True:
                intv = round(time.time() - start)
                MT_str = str(MT_port.read(35))
                AF_str = MT_str[5:8] + "." + MT_str[8:10]
                AP_str = MT_str[11:15]

                if MT_str[5] == "+" and MT_str[11] == "+":
                    data_AF.append(float(AF_str[1:5]))
                    data_AP.append(float(AP_str[1:4]))
                elif MT_str[5] == "+" and MT_str[11] != "+":
                    data_AF.append(float(AF_str[1:5]))
                    data_AP.append(float(AP_str[0:4]))
                elif MT_str[5] != "+" and MT_str[11] == "+":
                    data_AF.append(float(AF_str[0:5]))
                    data_AP.append(float(AP_str[1:4]))
                else:
                    data_AF.append(float(AF_str[0:5]))
                    data_AP.append(float(AP_str[0:4]))

                if intv%interval == 0:
                    #need to compute to more decimal places, if possible
                    AF_avg.append(np.mean(data_AF))
                    AP_avg.append(np.mean(data_AP))
                    ts_MT.append(intv)
                    data_AF, data_AP = [],[]
                else:
                    pass

        print(AF_avg, AP_avg, ts_MT)

#---------------------------
#kidney mass - force transducer

interval = 10
start = time.time()

with ser.Serial("COM4", 2400, timeout= 1000) as FT_1_port:
        data_FT_1 = []
        i = 1
        FT_1_avg, ts_FT_1 = [], []

        while True:
                intv = round(time.time() - start)           
                FT_1_str = str(FT_1_port.read(6))
                #write function to rearrange in case of misplaced string
                data_FT_1.append(float(FT_1_str[2:8]))

                if intv != 0 and intv%interval == 0 and i%10 == 0:
                       FT_1_avg.append(np.mean(data_FT_1))
                       ts_FT_1.append(intv)
                       data_FT_1 = []
                       i = 1
                else:
                       pass
                i += 1

print(FT_1_avg, ts_FT_1)
                         
#---------------------------
#BioTrend - sensor

start = time.time()

BT_port = ser.Serial("COM5", 9600, timeout= 1000)

while True:                  
        intv = time.time() - start   
        mod = intv%interval 
        BT_str = str(BT_port.read(43))
        print(BT_str)                         
                         
#---------------------------
#urine output - force transducer
                         
interval = 10
start = time.time()
                         

with ser.Serial("COM6", 2400, timeout= 1000) as FT_port_2:        
        data_FT_2 = []
        i = 1
        FT_2_avg, ts_FT_2 = [],[]

        while True:
                intv = round(time.time() - start)           
                FT_2_str = str(FT_2_port.read(6))
                data_FT_2.append(float(FT_2_str[2:8])

                if intv != 0 and intv%interval == 0 and i%10 == 0:
                       FT_2_avg.append(np.mean(data_FT_2))
                       ts_FT_2.append(time.ctime())
                       data_FT_2 = []
                       i = 1
                else:
                       pass
                i += 1

        print(FT_2_avg, ts_FT_2)
