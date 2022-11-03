#notes:
#set data rate at 0.2 Hz

def hours_to_sec(t_hrs):
    t_secs = 3600*t
    return t_secs

PERFUSION_LENGTH = hours_to_sec(8)

#necessary libraries
import serial as ser
import threading
import numpy as np
import time
import pandas as pd
import matplotlib as plt

#integrating multiple ports at once, threading
#initialize
MT = ser.Serial("COM5", 9600, timeout=1000)
FT_1 = ser.Serial("COM4", 2400, timeout=1000)
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
        if (lap_FT_1%5 == 0 and lap_FT_1 != 0) and FT_1_str[4] == ".":
            if i == j:
                j += 75
                pass
            else:
                print(f"{FT_1_str[2:8]} {lap_FT_1-5}")
        i += 1

#sO2 and hct
def BT_port(init):
    while init <= PERFUSION_LENGTH
        with ser.Serial("COM3", 9600, timeout=1000) as BT:
            end_BT = time.time()
            lap_BT = round(end_BT - init)
            BT_byte = s.read(43)
            BT_str = str(BT_byte)
            print(f"{BT_str[2:43]} {lap_BT}")
        time.sleep(5)
        init += 1
    
MT_thread = threading.Thread(target=MT_port, args=(MT,start),)
FT_1_thread = threading.Thread(target=FT_1_port, args=(FT_1_,start),)
BT_thread = threading.Thread(target=BT_port, args=(start),)

MT_thread.start()
FT_1_thread.start()
BT_thread.start()

MT_thread.join()
FT_1_thread.join()
BT_thread.join()

MT.close()
FT_1.close()
