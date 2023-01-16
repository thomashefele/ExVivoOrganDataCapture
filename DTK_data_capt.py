import serial as ser, numpy as np, simpleaudio as sa
import pyodbc, serial.tools.list_ports, platform
from time import time, sleep
from threading import Thread

#Set up info needed for threads:
#The baud rates for the force transducers are 2400 and 9600 while conditionals below retreive the serial port names. The os assigns port names
#incrementally and can retreive the serial no. of each driver for each USB port. However, it is not possible to discern which serial no. belongs
#to which cable, so the alternative is plugging the devices in the following order:
#- Bioconsole
#- Biotrend
#- Force transducers (order doesn't matter)
#from this, the devices will be assigned sequentially and then this sequence can be retreived via the conditional below for the threadings, allowing for
#a plug-and-play data collection, so long as the order for device plug in is followed. It is important that no other USB devices are plugged in (or at 
#least are plugged in after the sequence above) so as to not interfere with the plug-and-play sequencing.
Nusb, lap = 0, 5
baud_rate, t_o = [9600, 2400], [5.15, 5.25, 0.25]

while Nusb != 4:
        name = []
        ports = serial.tools.list_ports.comports()
        for dev,descr,hwid in sorted(ports):
                if dev.find("COM") != -1 or dev.find("USB") != -1 or dev.find("usbserial") != -1:
                        name.append(dev)
                else:
                        pass
        Nusb = len(name)

null_input = "b\'\'"
nan = float("nan")

#Establish database connection
connString = ""
OS = platform.system()

if OS == "Linux":
    dsn = "DTKserverdatasource"
    user = "dtk_lab@dtk-server"
    password = "data-collection1"
    database = "perf-data"
    connString = "DSN={0};UID={1};PWD={2};DATABASE={3};".format(dsn,user,password,database)
elif OS == "Windows":
    server = "dtk-server.database.windows.net"
    database = "perf-data"
    username = "dtk_lab"
    password = "data-collection1"
    connString = "DRIVER={SQL Server};SERVER={0};DATABASE={1};UID={2};PWD={3}".format(server,database,username,password)

#This block of code retrieves the UNOS ID from the organ donor database so that it may be associated to all other data collected.
with pyodbc.connect(connString) as cnxn_unos:
        with cnxn_unos.cursor() as cursor:
                cursor.execute("SELECT TOP 1 UNOS_ID FROM dbo.organ_t ORDER BY time_stamp DESC;") 
                row = cursor.fetchone()

#This initializes the warning sound to be played if a sensor falls asleep
N = 44100
T = 0.25
x = np.linspace(0, int(T*N),  N, False)
aud = np.sin(600 * x * 2 * np.pi)
aud *= 32767/np.max(np.abs(aud))
aud = aud.astype(np.int16)

#Needed for force transducer, as sometimes it prints in a "shifted" format due to an initial hexadecimal that occasionally appears and thus the data needs 
#to be rearranged into the proper format.
def rearrange(str):
    ordered = []
    new_str = ""
    l = len(str)
    if str[2] != ".":
        if str[0] == ".":
            for i in range(l):
                ordered.append(str[(i+4)%l])
                new_str += ordered[i]
        elif str[1] == ".":
            for i in range(l):
                ordered.append(str[(i+5)%l])
                new_str += ordered[i]
        elif str[3] == ".":
            for i in range(l):
                ordered.append(str[(i+1)%l])
                new_str += ordered[i]
        elif str[4] == ".":
            for i in range(l):
                ordered.append(str[(i+2)%l])
                new_str += ordered[i]
        elif str[5] == ".":
            for i in range(l):
                ordered.append(str[(i+3)%l])
                new_str += ordered[i]
    else:
        new_str = str

    return float(new_str)

#This function parses the data output from the Biotrend device to retreive the venous sO2 and the hematocrit during perfusion. Due to the presence of
#hexadecimal characters at times at the beginning of the data output, this function searches for certain characters and then locates the values based on
#those characters. This is in contrast to other functions which parses the known indices of values and reports at those indices. It has been encountered in
#the past that hexadecimal characters appear in the middle of the data string, but it has not occurred with the current driver/cable pairing, so the 
#function below only accounts for the current hexadecimal anomaly encountered.
def data_check(data_str):
    
    if data_str == null_input:
        #alert = sa.play_buffer(aud, 1, 2, N)
        O2_sat, hct = nan, nan
    else:
        sO2_start = data_str.find("SO2=")
        hct_start = data_str.find("HCT=")
        
        try:
                O2_str = data_str[(sO2_start+5):(sO2_start+7)]
                
                if O2_str == "--":
                        O2_sat = nan
                else:
                        O2_sat = float(O2_str)
                                
        except (IndexError, TypeError):
                O2_sat = nan
                
        try:
                hct_str = data_str[(hct_start+5):(hct_start+7)]
                
                if hct_str == "--":
                        hct = nan
                else:
                        hct = float(hct_str)
                                
        except (IndexError, TypeError):
                hct = nan
                
    return O2_sat, hct

#Medtronic Bioconsole sensor function. The MT_port.write method allows one to send a command to the Bioconsole in order to set the data rate output.
def MT(port_name, b, t):
    with pyodbc.connect(connString) as cnxn_MT:
        with cnxn_MT.cursor() as cursor:
            with ser.Serial(port_name, baudrate= b, timeout= t) as MT_port:                                              
                MT_port.write(b"DR 05 013B\r")

                while STOP == False:
                    MT_str = str(MT_port.read(35)) 
                        
                    if MT_str == null_input:
                        #alert = sa.play_buffer(aud, 1, 2, N)
                        execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(row[0])
                        cursor.execute(execstr)
                    else:
                        try:
                                AF_str = MT_str[5:8] + "." + MT_str[8:10]
                                AP_str = MT_str[11:15]

                                if MT_str[5] == "+" and MT_str[11] == "+":
                                        data_AF = float(AF_str[1:6])
                                        data_AP = float(AP_str[1:4])
                                elif MT_str[5] == "+" and MT_str[11] != "+":
                                        data_AF = float(AF_str[1:6])
                                        data_AP = float(AP_str[0:4])
                                elif MT_str[5] != "+" and MT_str[11] == "+":
                                        data_AF = float(AF_str[0:6])
                                        data_AP = float(AP_str[1:4])
                                else:
                                        data_AF = float(AF_str[0:6])
                                        data_AP = float(AP_str[0:4])
                                
                                execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure]) VALUES('{}', GETDATE(), {}, {});".format(row[0], data_AF, data_AP)
                                cursor.execute(execstr)
                        except (IndexError, ValueError, TypeError):
                                execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(row[0])
                                cursor.execute(execstr)
                    
                    cnxn_MT.commit()   

#Medtronic Biotrend sensor function                                                  
def BT(port_name, b, t):
    with pyodbc.connect(connString) as cnxn_BT:
        with cnxn_BT.cursor() as cursor:
            with ser.Serial(port_name, baudrate= b, timeout= t) as BT_port:

                while STOP == False:
                    BT_str = str(BT_port.read(43))
                    data_sO2v, data_hct = data_check(BT_str)
                
                    if np.isnan(data_sO2v) and np.isnan(data_hct):
                        execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(row[0])
                        cursor.execute(execstr)
                    elif np.isnan(data_sO2v) == True and np.isnan(data_hct) == False:
                        execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [hct]) VALUES('{}', GETDATE(), {});".format(row[0], data_hct)
                        cursor.execute(execstr)
                    elif np.isnan(data_sO2v) == False and np.isnan(data_hct) == True:
                        execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2]) VALUES('{}', GETDATE(), {});".format(row[0], data_sO2v)
                        cursor.execute(execstr)
                    else:
                        execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{}', GETDATE(), {}, {});".format(row[0], data_sO2v, data_hct)
                        cursor.execute(execstr)
                            
                    cnxn_BT.commit()
          
#Force transducer sensor function. The force transducer outputs rate at a frequency of 10 Hz. The "interval" parameter allows us to set at what time
#interval at which we want to collect data (i.e. every x seconds). At the interval mark, the function iterates over the 10 data points sent, appends them
#to a data array and reports the average of these values as the value for that interval. At times, the force transducer (for an unknown reason) will report
#two averages. (Both are the same, so there is no error technically, we just want to avoid redundanceies in data reporting) In order to circumvent this 
#anomaly, I set a "check" that is set equal to the time interval at the end of the first data reporting. If a second, anomalous average is present, it will
#not be reported as the check is now equal to the interval, which causes the data reporting to be bypassed due to the first "if" conditional.
def FT(port_name, b, t, interval, measure):
        with pyodbc.connect(connString) as cnxn_FT:
                with cnxn_FT.cursor() as cursor:
                        with ser.Serial(port_name, baudrate= b, timeout= t) as FT_port:
                                data_FT = []
                                start = time()
                                i, check = 1, 0

                                while STOP == False:
                                    intv = round(time() - start)                                                                                           
                                    FT_str = str(FT_port.read(6))
                               
                                    if intv != 0 and (intv%5 == 0 or (intv+1)%5 == 0 or (intv-1)%5 == 0):
                                        if FT_str == null_input:
                                            data_FT.append(nan)
                                        else:
                                            data_FT.append(float(rearrange(FT_str[2:8])))

                                        if (i == 10 and check != intv) or (data_FT.count(nan) != 0 and check != intv):
                                            FT_avg = round(np.mean(data_FT), 3)
                                            sleepy = np.isnan(FT_avg)
                                        
                                            if measure == "km":
                                                if sleepy:
                                                    #alert = sa.play_buffer(aud, 1, 2, N)
                                                    execstr = "INSERT INTO dbo.km_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(row[0])
                                                    cursor.execute(execstr)
                                                else:
                                                    execstr = "INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{}', GETDATE(), {});".format(row[0], FT_avg)
                                                    cursor.execute(execstr)
                                            elif measure == "uo":
                                                if sleepy:
                                                    #alert = sa.play_buffer(aud, 1, 2, N)
                                                    execstr = "INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(row[0])
                                                    cursor.execute(execstr)
                                                else:
                                                    execstr = "INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp], [urine_output]) VALUES('{}', GETDATE(), {});".format(row[0], FT_avg)
                                                    cursor.execute(execstr)
                                            cnxn_FT.commit()
                                            i, check = 0, intv
                                            del data_FT[:]
                                        
                                        if data_FT.count(nan) != 0 and check == intv:
                                            i = 0 
                                            del data_FT[:]
                                            
                                        i += 1
                                    else:
                                        pass
                                      
#The Biotrend device, for an unknown reason, tends to output a "shifted" line of data due to the presence of a NULL hexadecimal character (\x00) at the
#beginning of the data line. If the program is terminated and restarted, the shift disappears (possibly an inevitable start up anomaly). The "degunker"
#function below opens an initial thread to read the abnormal data line and then closes, allowing the subsequent "BT" function to read data without any
#hexadecimal abnormalities.                                
def degunker(port_name, b, t):
        with ser.Serial(port_name, baudrate= b, timeout= t) as degunk_port:
            diff = 0
            start = time()
            while diff < 10:
                BT_str = str(degunk_port.read(43))
                diff = time() - start
                 
degunk_thread = Thread(target= degunker, args= (name[1], baud_rate[0], t_o[1]),)
degunk_thread.start()
degunk_thread.join() 

#Here is where the threads for all the data collection functions are commenced and subsequently terminated. The threads cannot be terminated manually
#without raising an error, so a global STOP variable has been set that, when a certain time is reached, is set to TRUE. Within each thread, this causes a 
#termination of the loops of each function.
MT_thread = Thread(target= MT, args= (name[0], baud_rate[0], t_o[0]),)
BT_thread = Thread(target= BT, args= (name[1], baud_rate[0], t_o[1]),)
FT_1_thread = Thread(target= FT, args= (name[2], baud_rate[1], t_o[2], lap, "km"),)
FT_2_thread = Thread(target= FT, args= (name[3], baud_rate[1], t_o[2], lap, "uo"),)

STOP = False
perf_time = 30000
t_start = time()
del_t = 0

MT_thread.start()
BT_thread.start()
FT_1_thread.start()
FT_2_thread.start()

while del_t <= perf_time:                                
    del_t = time()-t_start

STOP = True
