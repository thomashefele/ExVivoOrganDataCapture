import serial as ser
import time
import numpy as np
from math import floor
from threading import Thread
import pandas as pd
        
lap = 10
name = ["COM3", "COM4", "COM5", "COM6"]
baud_rate = [9600, 2400, 9600, 2400]
t_o = 1000
start = time.time()
#reassign below as scalars to pass to cloud in future
AF_avg, AP_avg, FT_1_avg, sO2v_avg, hct_avg, FT_2_avg = [],[],[],[],[],[]
ts_MT, ts_FT_1, ts_BT, ts_FT_2 = [],[],[],[]

def MT(port_name, b, t, interval):
        MT_port = ser.Serial(port_name, baud= b, timeout= t)
        MT_port.write(b"DR 01 0137\r")
        data_AF, data_AP = [],[]
        global AF_avg, AP_avg, ts_MT
        check = 0
        
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
                
                if intv%interval == 0 and check != intv:
                    #figure out if need to calculate to more decimal places
                    AF_avg.append(np.mean(data_AF))
                    AP_avg.append(np.mean(data_AP))
                    ts_MT.append(intv)
                    data_AF, data_AP = [],[]
                    check = intv
                else:
                        pass
                

def FT_1(port_name, b, t, interval):
        FT_1_port = ser.Serial(port_name, baud= b, timeout= t)
        data_FT_1 = []
        i = 1
        global FT_1_avg, ts_FT_1
        check = 0        
        #write function to rearrange data if stream is 'offshifted'
        while True:
                intv = round(time.time() - start)           
                FT_1_str = str(FT_1_port.read(6))
                data_FT_1.append(float(FT_1_str[2:8]))

                if intv != 0 and intv%interval == 0 and i%10 == 0 and check != intv:
                       FT_1_avg.append(np.mean(data_FT_1))
                       ts_FT_1.append(intv)
                       data_FT_1 = []
                       i = 1
                       check = intv
                else:
                       pass
                i += 1
                

def BT(port_name, b, t, interval):
        BT_port = ser.Serial(port_name, baud= b, timeout= t)
        N = 1
        data_sO2v, data_hct = [],[]                               
        global sO2v_avg, hct_avg, ts_BT
        while True:
                intv = time.time() - start
                mod = intv%interval 
                BT_str = str(BT_port.read(43))
                #change below when data is available during trial perfusion
                #data_sO2v.append(BT_str[12:14]))
                #data_hct.append(BT_str[20:22]))
                #change "0" to data_...[-1] during trial perfusion 
                if BT_str[12:14] == "--" and BT_str[20:22] == "--":
                        data_sO2v.append(0)
                        data_hct.append(0)               
                if mod >= 5 and mod <= 10:
                       sO2v_avg.append(np.mean(data_sO2v))
                       hct_avg.append(np.mean(data_hct))         
                       ts_BT.append(10*N)
                       data_FT_1 = []
                       N += 1
                else:
                       pass                     

def FT_2(port_name, b, t, interval):
        FT_2_port = ser.Serial(port_name, baud= b, timeout= t)
        data_FT_2 = []
        i = 1
        global FT_2_avg, ts_FT_2
        check = 0
        #write function to rearrange data if stream is 'offshifted'     
        while True:
                intv = round(time.time() - start)           
                FT_2_str = str(FT_2_port.read(6))
                data_FT_2.append(float(FT_2_str[2:8]))

                if intv != 0 and intv%interval == 0 and i%10 == 0:
                       FT_2_avg.append(np.mean(data_FT_2))
                       ts_FT_2.append(intv)
                       data_FT_2 = []
                       i = 1
                       check = intv 
                else:
                       pass
                i += 1
        

MT_thread = Thread(target= MT, args= (name[0], baud_rate[0], t_o, lap),)
FT_1_thread = Thread(target= FT_1, args= (name[1], baud_rate[1], t_o, lap),)
BT_thread = Thread(target= BT, args= (name[2], baud_rate[2], t_o, lap),)
FT_2_thread = Thread(target= FT_2, args= (name[3], baud_rate[3], t_o, lap),)

MT_thread.start()
FT_1_thread.start()
BT_thread.start()
FT_2_thread.start()

MT_thread.join()
FT_1_thread.join()
BT_thread.join()
FT_2_thread.join()

df = pd.DataFrame({"Arterial Flow (L/min)": AF_avg, "Arterial Pressure (mmHg)": AP_avg, "Kidney Mass (kg)": FT_1_avg, "sO2": sO2v_avg, 
                   "Hct": hct_avg, "Urine Output (kg)": FT_2_avg, "Time 1": ts_MT, "Time 2": ts_FT_1, "Time 3": ts_BT, "Time 4": ts_FT_2})
print(df)
