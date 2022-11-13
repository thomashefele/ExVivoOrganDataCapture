#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import serial as ser
import time
import numpy as np
import scipy as sp
import threading
import matplotlib as plt
import pandas as pd
        
lap = 10
name = ["COM3", "COM4", "COM5", "COM6"]
baud_rate = [9600, 2400, 9600, 2400]
t_o = 1000
data_MT_AF, data_MT_AP, data_FT_1, data_BT_sO2v, data_BT_hct data_FT_2 = [], [], [], [], [], []
AF_avg, AP_avg, FT_1_avg, sO2v_avg, hct_avg, FT_2_avg = 0,0,0,0,0,0

def MT(port_name, b, t, interval):
        MT_port = ser.serial(port_name, baud= b, timeout= t)
        MT_port.write(
        global data_MT_AF, data_MT_AP, AF_avg, AP_avg
        
        while True:
                
        return

def FT_1(port_name, b, t, interval):
        FT_1_port = ser.serial(port_name, baud= b, timeout= t)
        return

def BT(port_name, b, t, interval):
        BT_port = ser.serial(port_name, baud= b, timeout= t)
        return

def FT_2(port_name, b, t, interval):
        FT_2_port = ser.serial(port_name, baud= b, timeout= t)
        return

MT_thread = threading.Thread(target= MT, args= (name[0], baud_rate[0], t_o, lap),)
FT_1_thread = threading.Thread(target= FT_1, args= (name[1], baud_rate[1], t_o, lap),)
BT_thread = threading.Thread(target= BT, args= (name[2], baud_rate[2], t_o, lap),)
FT_2_thread = threading.Thread(target= FT_2, args= (name[3], baud_rate[3], t_o, lap),)

MT_thread.start()
FT_1_thread.start()
BT_thread.start()
FT_2_thread.start()

MT_thread.join()
FT_1_thread.join()
BT_thread.join()
FT_2_thread.join()
