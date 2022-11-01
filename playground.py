#notes:
#set data rate at 0.2 Hz
#first two hours - normalization phase: "show me (?)" data yields a certain set of parameters that can be fitted to a model. Deviations from model yield information about health of kidney
#intervention phase followed by differential phase

#integrating multiple ports at once, threading
import serial as ser
import threading
import numpy as np

#initialize
MT = ser.Serial("COM3", 9600, timeout=1000)
FT_1 = ser.Serial("COM4", 2400, timeout=1000)
start = time.time()

#threading functions
#arterial flow and pressure
def MT_port(s, init):
    s.write(b'DR 05 013C\r')
    while True:
        try:
            end_MT = time.time()
            lap_MT = round(end_MT - init)
            MT_byte = s.read(35)
            MT_str = str(MT_byte)
            print(f"{MT_str[5:15]} {lap_MT}")
        except KeyboardInterrupt:
            break
        if s.in_waiting() is False:
            break
        else:
            pass
#kidney mass            
def FT_port(s, init):
    iterable = 0
    while True:
        try:
            end_MT = time.time()
            lap_FT = round(end_MT - init)
            FT_byte = s.read(16)
            FT_str = str(FT_byte)
            if iterable%50 == 0:
                print(f"{FT_str[2:8]} {lap_FT}")
        except KeyboardInterrupt:
            break
        if s.in_waiting() is False:
            break
        else:
            pass
        iterable += 1

MT_thread = threading.Thread(target=MT_port, args=(MT,),).start()
FT_1_thread = threading.Thread(target=FT_port, args=(FT_1,),).start()

MT_thread.join()
FT_1_thread.join()

MT.close()
FT_1.close()

#after integration, real time data collection and graphical display

