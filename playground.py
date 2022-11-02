#notes:
#set data rate at 0.2 Hz

#necessary libraries
import serial as ser
import threading
import numpy as np
import time
import pandas as pd
import matplotlib as plt

#integrating multiple ports at once, threading
#initialize
#MT = ser.Serial("COM5", 9600, timeout=1000)
#FT_1 = ser.Serial("COM4", 2400, timeout=1000)
BT = ser.Serial("COM3", 9600, timeout=1000)
start = time.time()
#MT.write(b'DR 051 013B\r')

#threading functions
#arterial flow and pressure
def MT_port(s, init):
    while True:
        end_MT = time.time()
        lap_MT = round(end_MT - init)
        MT_byte = s.read(35)
        MT_str = str(MT_byte)
        print(f"{MT_str[5:15]} {lap_MT}")

#kidney mass            
def FT_1_port(s, init):
    i = 0
    j = 39
    while True:
        end_FT = time.time()
        lap_FT = round(end_FT - init)
        FT_byte = s.read(16)
        FT_str = str(FT_byte)
        if (lap_FT%5 == 0 and lap_FT != 0) and FT_str[4] == ".":
            if i == j:
                j += 75
                pass
            else:
                print(f"{FT_str[2:8]} {lap_FT-5}")
        i += 1

#sO2 and hct
def BT_port(s, init):
    old_lap = 0
    while True:
        end_BT = time.time()
        lap_BT = end_BT - init
        delta = lap_BT - old_lap
        BT_byte = s.read(43)
        BT_str = str(BT_byte)
        if round(lap_BT) != 0:
            print(f"{BT_str[2:43]} {round(lap_BT)} {delta}")
        old_lap = lap_BT
        
#MT_thread = threading.Thread(target=MT_port, args=(MT,start),)
#FT_1_thread = threading.Thread(target=FT_port, args=(FT_1,start),)
BT_thread = threading.Thread(target=BT_port, args=(BT,start),)

#MT_thread.start()
#FT_1_thread.start()
BT_thread.start()

#MT_thread.join()
#FT_1_thread.join()
BT_thread.join()

#MT.close()
#FT_1.close()
BT.close()
