#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#integrating multiple ports at once, traditional looping 
import serial as ser
import time

#initialize
MT = ser.Serial("COM3", 9600, timeout=1000)
FT_1 = ser.Serial("COM4", 2400, timeout=1000)
iterable = 0
start = time.time()
MT.write(b'DR 01 0137\r')

#looping conditional
while MT.in_waiting() is True and FT_1.in_waiting() is True: 
    try:
        #time
        end = time.time()
        lap = round(end - start)
        #arterial flow and pressure
        MT_byte = MT.read(35)
        MT_str = str(MT_byte)
        #kidney mass
        FT_byte = FT_1.read(35)
        FT_str = str(FT_byte)
        if iterable%10 == 0:
            print(f"{lap}, {MT_str[5:15]}, {FT_str[2:8]}")
        else:
            pass
    except KeyboardInterrupt:
        break
    except SerialException:
        break
    iterable += 1
MT.close()
FT_1.close()


# In[ ]:


#integrating multiple ports at once, threading
import serial as ser
import threading
import numpy as np

#initialize
MT = ser.Serial("COM3", 9600, timeout=1000)
FT_1 = ser.Serial("COM4", 2400, timeout=1000)
array1, array2, array3 = [], [], []
start = time.time()
end_MT, end_FT = 0,0

#threading functions
#arterial flow and pressure
def MT_port(s):
    s.write(b'DR 01 0137\r')
    end_MT = time.time()
    while True:
        try:
            MT_byte = s.read(35)
            MT_str = str(MT_byte)
            array1.append(MT_str[5:10])
            array2.append(MT_str[11:15])
        except KeyboardInterrupt:
            break
        except SerialException:
            break
    return array1, array2, end_MT
#kidney mass            
def FT_port(s):
    iterable = 0
    end_FT = time.time()
    while True:
        try:
            FT_byte = s.read(16)
            FT_str = str(FT_byte)
            if iterable%10 == 0:
                array3.append(FT_str[2:8])
        except KeyboardInterrupt:
            break
        except SerialException:
            break
        iterable += 1
    return array3, end_FT

MT_thread = threading.Thread(target=MT_port, args=(MT,),).start()
FT_1_thread = threading.Thread(target=FT_port, args=(FT_1,),).start()

MT_thread.join()
FT_1_thread.join()

MT_elapsed = round(end_MT - start)
FT_1_elapsed = round(end_FT - start)

#key stats
array1
print(np.size(np.array(array1)))
array2
print(np.size(np.array(array2)))
array3
print(np.size(np.array(array3)))
MT_elapsed
FT_1_elapsed

MT.close()
FT_1.close()


# In[ ]:


#alternative/hybrid threading approach to integrating multiple ports at once
import serial as ser
import threading
import numpy as np

#initialize
MT = ser.Serial("COM3", 9600, timeout=1000)
FT_1 = ser.Serial("COM4", 2400, timeout=1000)

start = time.time()
data_MT_AF, data_MT_AP, data_FT = "","",""
iterable = 0

#threading functions
#arterial flow and pressure
def MT_port(s):
    MT_byte = s.read(35)
    MT_str = str(MT_byte)
    data_MT_AF, data_MT_AP = MT_str[5:10], MT_str[11:15]
    return data_MT_AF, data_MT_AP
#kidney mass             
def FT_port(s):
    FT_byte = s.read(16)
    FT_str = str(FT_byte)
    data_FT = FT_str[2:8]
    return

while MT.in_waiting() is True and FT_1.in_waiting() is True:
    try:
        MT_thread = threading.Thread(target=MT_port, args=(MT,),).start()
        FT_1_thread = threading.Thread(target=FT_port, args=(FT_1,iterable,),).start()
        MT_thread.join()
        FT_1_thread.join()
        end = time.time()
        lap = round(end - start)
        if iterable%10 == 0:
            print(f"{lap} {data_MT_AF} {data_MT_AP} {data_FT}")
        else:
            pass
        iterable += 1
    except KeyboardInterrupt:
        break
    except SerialException:
        break

MT.close()
FT_1.close()


# In[ ]:


#after integration, real time data collection and graphical display

