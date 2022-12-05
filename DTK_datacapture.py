import serial as ser
from time import localtime, asctime, time
from  numpy import mean
import pyodbc 
from threading import Thread

#establish database connection
server = "dtk-server.database.windows.net"
database = "perf-data"
username = "dtk_lab"
password = "data-collection1"
with pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password) as cnxn:
    with cnxn.cursor() as cursor:
        #set up info needed for threads
        unos_id = cnxn.execute("SELECT UNOS_ID FROM dbo.istat_t;")
        lap = 5
        name = ["COM3", "COM4", "COM5", "COM6"]
        baud_rate = [9600, 2400, 9600, 2400]
        t_o = 1000
        #needed for force transducer, as sometimes it prints in a "shifted" format
        def rearrange(str):   
            ordered = []
            new_str = ""
            l = len(str)
            if str[2] != ".":
                if str[0] == ".":
                    for i in range(0,l):
                        ordered.append(str[(i+4)%l]
                        new_str += ordered[i]
                elif str[1] == ".":
                    for i in range(0,l):
                        ordered.append(str[(i + 5)%l)
                        new_str += ordered[i]
                elif str[3] == ".":
                    for i in range(0,l):
                        ordered.append(str[(i + 1)%l])
                        new_str += ordered[i]
                elif str[4] == ".":
                    for i in range(0,l):
                        ordered.append(str[(i + 2)%l])
                        new_str += ordered[i]
                elif str[5] == ".":
                    for i in range(0,l):
                        ordered.append(str[(i + 3)%l])
                        new_str += ordered[i]
            else:
                    new_str = str
                                           
            return float(new_str)

        #MedTronic console sensor function
        def MT(port_name, b, t):
            with ser.Serial(port_name, baud= b, timeout= t) as MT_port:                                              
                MT_port.write(b"DR 05 013B\r")
                data_AF, data_AP, ts_MT = None, None, None
                global STOP

                while True:
                    MT_str = str(MT_port.read(35))
                    ts_MT = asctime(localtime())                                
                    AF_str = MT_str[5:8] + "." + MT_str[8:10]
                    AP_str = MT_str[11:15]

                    if MT_str[5] == "+" and MT_str[11] == "+":
                        data_AF = float(AF_str[1:5])
                        data_AP = float(AP_str[1:4])
                    elif MT_str[5] == "+" and MT_str[11] != "+":
                        data_AF = float(AF_str[1:5])
                        data_AP = float(AP_str[0:4])
                    elif MT_str[5] != "+" and MT_str[11] == "+":
                        data_AF = float(AF_str[0:5])
                        data_AP = float(AP_str[1:4])
                    else:
                        data_AF = float(AF_str[0:5]))
                        data_AP = float(AP_str[0:4]))

                    cnxn.execute(f"INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure]) VALUES({unos_id}, {ts_MT}, {data_AF}, {data_AP})")
                                                
                    if STOP = True:
                        break
                                           
        #force transducer sensor function
        def FT(port_name, b, t, interval, measure):
            with ser.Serial(port_name, baud= b, timeout= t) as FT_port:
                data_FT = []
                start = time()
                FT_avg, ts_FT = None, None
                global STOP
                i = 1
                check = 0
                                           
                while True:
                    intv = round(time() - start)                                                                                                 
                    FT_1_str = str(FT_1_port.read(6))  
                    
                    if intv != 0 and intv%interval == 0:  
                        data_FT.append(float(rearrange(FT_1_str[2:8])))

                        if i%10 == 0 and check != intv:
                            ts_FT = asctime(localtime())
                            FT_avg = mean(data_FT)

                            if measure == "km":                           
                                cnxn.execute(f"INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES({unos_id}, {ts_FT}, {FT_avg})")
                            elif measure == "uo":
                                cnxn.execute(f"INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp], [urine_output]) VALUES({unos_id}, {ts_FT}, {FT_avg})")
                            
                           data_FT = []
                           i = 1
                           check = intv               
                        else:
                            pass
                        i += 1
                        
                    if STOP = True:
                        break
                                           
        #MedTronic BioTrend sensor function                                                  
        def BT(port_name, b, t):
            with ser.Serial(port_name, baud= b, timeout= t) as BT_port:
                data_sO2v, data_hct, ts_BT = None, None, None
                global STOP

                while True:
                    BT_str = str(BT_port.read(43))
                    ts_BT = asctime(localtime())                             
                    data_sO2v = float(BT_str[12:14]))
                    data_hct = float(BT_str[20:22]))

                    if BT_str[12:14] == "--":
                        data_sO2v = 0                                              
                    if BT_str[20:22] == "--":
                        data_hct = 0
                    cnxn.execute(f"INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES({unos_id}, {ts_BT}, {data_sO2v}, {data_hct})")
                                           
                    if STOP = True:
                        break

        #establish threads, run threads, and end threads
        MT_thread = Thread(target= MT, args= (name[0], baud_rate[0], t_o),)
        FT_1_thread = Thread(target= FT, args= (name[1], baud_rate[1], t_o, lap, "km"),)
        BT_thread = Thread(target= BT, args= (name[2], baud_rate[2], t_o),)
        FT_2_thread = Thread(target= FT, args= (name[3], baud_rate[3], t_o, lap, "uo"),)
                                           
        STOP = False
        perf_time = 28800
        t_start = time()
        del_t = None
                                           
        MT_thread.start()
        FT_1_thread.start()
        BT_thread.start()
        FT_2_thread.start()
                                           
        while del_t < perf_time:                                
            del_t = time()-t_start       
        STOP = True

        MT_thread.join()
        FT_1_thread.join()
        BT_thread.join()
        FT_2_thread.join()
