import serial as ser, numpy as np, simpleaudio as sa, pandas as pd
import pyodbc, serial.tools.list_ports, os, sys, platform, csv
from time import monotonic, sleep
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox
from threading import Thread
from pandastable import Table

no_fitz = False

try:
    import fitz
except ImportError:
    no_fitz = True
    
lap, perf_time, name, baud_rate, t_o = 5, 30000, [], [9600,2400], [5.1, 5.2, 0.2]
CHOOSE_AGN, CHECK_AGAIN = False, False
null_input, nan, connString, execstr  = "b\'\'", float("nan"), "", ""
OS = platform.system()

#The code below establishes the necessary information to interact with the given OS. Note: SQL drivers have been tricky to install on Mac (at least those
#with the M1 chip). As such, the software on Mac will not connect to the Azure database but rather will write all data to CSV files which can then be
#uploaded to the database post-perfusion.
if OS == "Linux":
    dsn = "DTKserverdatasource"
    user = "dtk_lab@dtk-server"
    password = "data-collection1"
    database = "perf-data"
    connString = "DSN={0};UID={1};PWD={2};DATABASE={3};".format(dsn,user,password,database)

elif OS == "Windows":
    driver = "{SQL Server}"
    server = "dtk-server.database.windows.net"
    database = "perf-data"
    username = "dtk_lab"
    password = "data-collection1"
    connString = "DRIVER={0};SERVER={1};DATABASE={2};UID={3};PWD={4}".format(driver,server,database,username,password)

def app(UNOS_AGAIN= None):
    root = Tk()
    root.withdraw()
    root.title("Kidney Perfusion App")
    
    #Unit testing of file writer and database connection
    if UNOS_AGAIN == "Y":
        file_unit, db_unit = True, True
        start_msg = "The following issues exist:\n\n"

        try:
            with open("test_file.csv", "a") as file:
                a = csv.writer(file)
                a.writerow(["Test"])
            os.remove("test_file.csv")     
        except (PermissionError, OSError, IOError):
            file_unit = False
            start_msg += "- The file writing system does not\nhave permission to write on this system.\n\n"

        try:
            with pyodbc.connect(connString) as cnxn_test:
                with cnxn_test.cursor() as cursor:
                    execstr = "CREATE TABLE test(TEST text)"
                    cursor.execute(execstr)
                    cnxn_test.commit()
                    execstr = "DROP TABLE test"
                    cursor.execute(execstr)
                    cnxn_test.commit()
        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
            db_unit = False
            start_msg += "- The database connection\nwas not established.\nCheck the following:\n\n1.) Firewall access\n2.) SQL driver\n3.) Internet connection\n4.) Wifi security"

        if file_unit == True and db_unit == True:
            start_msg = "Database connection and backup system successful!"

        messagebox.showinfo("Start Up", start_msg)
    else:
        pass
    
    root.deiconify()
    
    #The block of code below sets up the initial screen/GUI for the app. The program was originally designed for an 800x480 Raspberry Pi and tested 
    #on a 1440x900 MacBook so those are the standards for initializing the GUI screen size.
    w,h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.call("tk", "scaling", 1.0)
    root.attributes("-fullscreen", True)  
    root.config(bg= "RoyalBlue1")
    head_sz, txt_sz = 10, 10
    of_x,of_y = 0.37, 0.95
    df_x,df_y = 0.57, 0.95
    cf_x,cf_y = 0.34, 0.4
    radx = 0.2
    uf_x,uf_y = 0.34, 0.32
    don_x,don_y = 0.53, 0.8
    don_up, don_yes = 0.42, 0.7
    chemf_x,chemf_y = 0.255, 0.7
    med_y = 0.13
    sub_med, med_yes = 0.76, 0.75
    prt_x,prt_y = 0.54, 0.29
    prt_padx = 110
    disp_x,disp_y = 0.54, 0.53
    val_x,val_y = 0.45, 0.35
    tsx = 0.85
    chemsub_pady = 5
    istat_relx,pic_relx = 0.5, 0.5
    istat_rely,pic_rely = 0.7, 0.95
    av_label,opt_label = 10, 20
    allset_pad = 10
    u_pady, sub_pad,rest_pad,ex_pad = 10, 1, 1, 5
    perf_pad, biop_pad = 5, 10

    if w >= 1440 and h >= 900:
        head_sz, txt_sz = 25, 20
        of_x,of_y = 0.36, 0.95
        df_x,df_y = 0.61, 0.95
        cf_x,cf_y = 0.34, 0.42
        radx = 0.25
        uf_x,uf_y = 0.34, 0.38
        don_x,don_y = 0.59, 0.8
        don_up, don_yes = 0.375, 0.6
        chemf_x,chemf_y = 0.29, 0.72
        med_y = 0.15
        sub_med, med_yes = 0.78, 0.63
        prt_x,prt_y = 0.59, 0.25
        prt_padx = 160
        disp_x,disp_y = 0.59, 0.6
        val_x,val_y = 0.5, 0.4
        tsx = 0.75
        chemsub_pady = 15
        istat_relx,pic_relx = 0.48, 0.525
        istat_rely,pic_rely = 0.95, 0.8
        av_label,opt_label = 20, 50
        allset_pad = 45
        u_pady, sub_pad,rest_pad,ex_pad = 25, 5, 5, 15
        perf_pad, biop_pad = 35, 20

    var,unos_txt,exp_type = StringVar(), StringVar(), StringVar()
    header,txt = ("Helvetica", head_sz, "bold"), ("Helvetica", txt_sz)

    #This initializes the warning sound to be played if a sensor falls asleep.
    N = 44100
    T = 0.25
    x = np.linspace(0, T*N,  N, False)
    aud = np.sin(600 * x * 2 * np.pi)
    aud *= 32767/np.max(np.abs(aud))
    aud = aud.astype(np.int16)
    
    #This function acts as a CSV file writer that serves as a backup for the SQL database in the case that a connectivity error (unsuitable driver,
    #no firewall access, no internet connection, etc.) arises during the perfusion so that no data is lost.
    def file_write(file_name, h_array, r_array):
        h = False
        
        try:
            with open(file_name, "r") as file:
                r = csv.reader(file)
                h_row = next(r)

                if h_row == h_array:
                    h = True
                    
        except FileNotFoundError:
            pass
        
        with open(file_name, "a") as file:
            a = csv.writer(file)
            
            if h == False:
                a.writerow(h_array)

            a.writerow(r_array)

    #Function that sounds  warning if one of the sensors falls asleep
    def alert():
        try:
            try:
                warn = sa.play_buffer(aud, 1, 2, N)
            except _sa.SimpleaudioError:
                pass
        except NameError:
            pass

    #Functions called by GUI to restart or quit program.
    def anew():
        global CHOOSE_AGN
        global CHECK_AGAIN
        global STOP
        CHOOSE_AGN, CHECK_AGAIN, STOP = False, False, True
        root.destroy()
        app()

    def q(tipo):
        global STOP
        STOP = True

        if tipo == "data":
            Label(disp_w, text= "Data collection complete. Goodbye!", font= txt, padx= 100).place(relx= 0.5, rely= 0.2, anchor= CENTER)
        elif tipo == "set":
            root.destroy()

    #Needed for force transducer, as sometimes it prints in a "shifted" format due to an initial hexadecimal that occasionally appears and thus 
    #the data needs to be rearranged into the proper format.
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

    #This function parses the data output from the Biotrend device to retrieve the venous sO2 and the hematocrit during perfusion. Due to the 
    #presence of hexadecimal characters at times at the beginning of the data output, this function searches for certain characters and then 
    #locates the values based on those characters. This is in contrast to other functions which parses the known indices of values and reports 
    #at those indices. It has been encountered in the past that hexadecimal characters appear in the middle of the data string, but it has not 
    #occurred with the current driver/cable pairing, so the function below only accounts for the current hexadecimal anomaly encountered.
    def data_check(data_str):
        O2_sat, hct = nan, nan

        def finder(pars_str, key):
            start = pars_str.find(key)
            data = nan

            try:
                wanted_str = pars_str[(start+5):(start+7)]

                if wanted_str == "--":
                    pass
                else:
                    data = float(wanted_str)

            except (IndexError, TypeError, ValueError):
                alert()
            return data

        if data_str == null_input:
            alert()
        else:
            O2_sat, hct = finder(data_str, "SO2="), finder(data_str, "HCT=")

        return O2_sat, hct

    #Medtronic Bioconsole sensor function. The MT_port.write method allows one to send a command to the Bioconsole in order to set the data 
    #rate output.
    def MT(port_name, b, t):
        with ser.Serial(port_name, baudrate= b, timeout= t) as MT_port:                                              
            MT_port.write(b"DR 05 013B\r")
            fn = "{0}_{1}_mt_data.csv".format(unos_ID, c_or_t)
            head_row = ["UNOS_ID", "time_stamp", "flow", "pressure", "rpm"]

            while STOP == False:
                upload_status,file_status = True,True
                
                try:
                    if MT_port.is_open == False:
                        MT_port.open()
                        MT_port.write(b"DR 05 013B\r")

                    MT_str = str(MT_port.read(35))
                    up_time = datetime.utcnow()
                    data_row = [unos_ID, up_time, None, None, None]
                    
                    if MT_str == null_input:
                        alert()

                        try:
                            with pyodbc.connect(connString) as cnxn_MT:
                                with cnxn_MT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.mt_{0}([UNOS_ID], [time_stamp]) VALUES('{1}', GETDATE());".format(c_or_t, unos_ID)
                                    cursor.execute(execstr)
                                    cnxn_MT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False
                        
                        try:
                            file_write(fn, head_row, data_row)
                        except (PermissionError, OSError, IOError):
                            file_status = False
                            
                    else:
                        try:
                            AF_str = MT_str[5:8] + "." + MT_str[8:10]
                            AP_str = MT_str[11:15]
                            rpm = float(MT_str[16:20])

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

                            try:
                                with pyodbc.connect(connString) as cnxn_MT:
                                    with cnxn_MT.cursor() as cursor:
                                        execstr = "INSERT INTO dbo.mt_{0}([UNOS_ID], [time_stamp], [flow], [pressure], [rpm]) VALUES('{1}', GETDATE(), {2}, {3}, {4});".format(c_or_t, unos_ID, data_AF, data_AP, rpm)
                                        cursor.execute(execstr)
                                        cnxn_MT.commit()
                            except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                                upload_status = False

                            try:
                                file_write(fn, head_row, [unos_ID, up_time, data_AF, data_AP, rpm])
                            except (PermissionError, OSError, IOError):
                                file_status = False

                        except (IndexError, ValueError, TypeError):
                            alert()

                            try:
                                with pyodbc.connect(connString) as cnxn_MT:
                                    with cnxn_MT.cursor() as cursor:
                                        execstr = "INSERT INTO dbo.mt_{0}([UNOS_ID], [time_stamp]) VALUES('{1}', GETDATE());".format(c_or_t, unos_ID)
                                        cursor.execute(execstr)
                                        cnxn_MT.commit()
                            except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                                upload_status = False
                            
                            try:
                                file_write(fn, head_row, data_row)
                            except (PermissionError, OSError, IOError):
                                file_status = False

                except (OSError, FileNotFoundError):
                    MT_port.close()
                    alert()
                    sleep(5)

                    try:
                        with pyodbc.connect(connString) as cnxn_MT:
                            with cnxn_MT.cursor() as cursor:
                                execstr = "INSERT INTO dbo.mt_{0}([UNOS_ID], [time_stamp]) VALUES('{1}', GETDATE());".format(c_or_t, unos_ID)
                                cursor.execute(execstr)
                                cnxn_MT.commit()
                    except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                        upload_status = False
                    
                    up_time = datetime.utcnow()
                    data_row = [unos_ID, up_time, None, None, None]
                    
                    try:
                        file_write(fn, head_row, data_row)
                    except (PermissionError, OSError, IOError):
                        file_status = False
                
                ts_MT = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                
                if upload_status == True or file_status == True:
                    ts_MT.place(relx= tsx, rely= 0.2, anchor= CENTER)
                else:
                    pass

    #Medtronic Biotrend sensor function                                                  
    def BT(port_name, b, t):
        with ser.Serial(port_name, baudrate= b, timeout= t) as BT_port:
            fn = "{0}_{1}_bt_data.csv".format(unos_ID, c_or_t)
            head_row = ["UNOS_ID", "time_stamp", "sO2", "hct"]
            
            while STOP == False:
                upload_status,file_status = True,True
                
                try:
                    if BT_port.is_open == False:
                        BT_port.open()
                    
                    BT_str = str(BT_port.read(43))
                    up_time = datetime.utcnow()
                    data_sO2v, data_hct = data_check(BT_str)
                  
                    if np.isnan(data_sO2v) and np.isnan(data_hct):
                        try:
                            with pyodbc.connect(connString) as cnxn_BT:
                                with cnxn_BT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.bt_{0}([UNOS_ID], [time_stamp]) VALUES('{1}', GETDATE());".format(c_or_t, unos_ID)
                                    cursor.execute(execstr)
                                    cnxn_BT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False
                        
                        try:
                            file_write(fn, head_row, [unos_ID, up_time, None, None])
                        except (PermissionError, OSError, IOError):
                            file_status = False
                        
                    elif np.isnan(data_sO2v) == True and np.isnan(data_hct) == False:
                        try:
                            with pyodbc.connect(connString) as cnxn_BT:
                                with cnxn_BT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.bt_{0}([UNOS_ID], [time_stamp], [hct]) VALUES('{1}', GETDATE(), {2});".format(c_or_t, unos_ID, data_hct)
                                    cursor.execute(execstr)
                                    cnxn_BT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False
                        
                        try:
                            file_write(fn, head_row, [unos_ID, up_time, None, data_hct])
                        except (PermissionError, OSError, IOError):
                            file_status = False
                        
                    elif np.isnan(data_sO2v) == False and np.isnan(data_hct) == True:
                        try:
                            with pyodbc.connect(connString) as cnxn_BT:
                                with cnxn_BT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.bt_{0}([UNOS_ID], [time_stamp], [sO2]) VALUES('{1}', GETDATE(), {2});".format(c_or_t, unos_ID, data_sO2v)
                                    cursor.execute(execstr)
                                    cnxn_BT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False
                        
                        try:
                            file_write(fn, head_row, [unos_ID, up_time, data_sO2v, None])
                        except (PermissionError, OSError, IOError):
                            file_status = False
                        
                    else:
                        try:
                            with pyodbc.connect(connString) as cnxn_BT:
                                with cnxn_BT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.bt_{0}([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{1}', GETDATE(), {2}, {3});".format(c_or_t, unos_ID, data_sO2v, data_hct)
                                    cursor.execute(execstr)
                                    cnxn_BT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False             
                    
                        try:
                            file_write(fn, head_row, [unos_ID, up_time, data_sO2v, data_hct])
                        except (PermissionError, OSError, IOError):
                            file_status = False
                        
                except (OSError, FileNotFoundError):
                    BT_port.close()
                    alert()
                    sleep(5)
                    
                    try:
                        with pyodbc.connect(connString) as cnxn_BT:
                            with cnxn_BT.cursor() as cursor:
                                execstr = "INSERT INTO dbo.bt_{0}([UNOS_ID], [time_stamp]) VALUES('{1}', GETDATE());".format(c_or_t, unos_ID)
                                cursor.execute(execstr)
                                cnxn_BT.commit()
                    except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                        upload_status = False

                    up_time = datetime.utcnow()
                    
                    try:
                        file_write(fn, head_row, [unos_ID, up_time, None, None])
                    except (PermissionError, OSError, IOError):
                        file_status = False
                  
                ts_BT = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                
                if upload_status == True or file_status == True:
                    ts_BT.place(relx= tsx, rely= 0.4, anchor= CENTER)
                else:
                    pass

    #Force transducer sensor function. The force transducer outputs data at a variable frequency.. The "interval" parameter allows us to set the 
    #what time interval at which we want to collect data (i.e. every x seconds withing +/- 0.5 secs of x). The function collects the data point closest to the "x"
    #interval mark.
    def FT(port_name, b, t, interval, measure):
        with ser.Serial(port_name, baudrate= b, timeout= t) as FT_port:
            rd, check, mass, m_arr = 0, 0, 0, []
            start = monotonic()

            while STOP == False:
                upload_status,file_status = True,True
                intv = monotonic()-start
                rd = round(intv)

                if rd != 0 and rd%5 == 0:
                    try:
                        if FT_port.is_open == False:
                            FT_port.open()

                        FT_str = str(FT_port.read(6))

                        if FT_str == null_input:
                            pot_m = nan
                        else:                                                
                            pot_m = float(rearrange(FT_str[2:8]))
                    except (IndexError, ValueError, TypeError):
                        pot_m = nan
                    except (OSError, FileNotFoundError):
                        FT_port.close()
                        pot_m = nan

                    mod = intv%5

                    if mod >= 4.5 and mod < 5:
                        diff = 5-mod
                    else:
                        diff = mod

                    m_arr.append([diff, pot_m])
                    check = rd

                elif rd != 0 and m_arr != [] and check != rd:
                    mass = min(m_arr, key= lambda x: x[0])[1]
                    sleepy = np.isnan(mass)

                    fn = "{0}_{1}_{2}_data.csv".format(unos_ID, c_or_t, measure)
                    head_row = []

                    if measure == "km":
                        head_row = ["UNOS_ID", "time_stamp", "kidney_mass"]
                    elif measure == "uo":
                        head_row = ["UNOS_ID", "time_stamp", "urine_output"]

                    up_time = datetime.utcnow()

                    if sleepy:
                        alert()

                        try:
                            with pyodbc.connect(connString) as cnxn_FT:
                                with cnxn_FT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.{0}_{1}([UNOS_ID], [time_stamp]) VALUES('{2}', GETDATE());".format(measure, c_or_t, unos_ID)
                                    cursor.execute(execstr)
                                    cnxn_FT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False
                        
                        try:
                            file_write(fn, head_row, [unos_ID, up_time, None])
                        except (PermissionError, OSError, IOError):
                            file_status = False
                    else:
                        try:
                            with pyodbc.connect(connString) as cnxn_FT:
                                with cnxn_FT.cursor() as cursor:
                                    execstr = "INSERT INTO dbo.{0}_{1}([{2}], [{3}], [{4}]) VALUES('{5}', GETDATE(), {6});".format(measure, c_or_t, *head_row, unos_ID, mass)
                                    cursor.execute(execstr)
                                    cnxn_FT.commit()
                        except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                            upload_status = False
                        
                        try:
                            file_write(fn, head_row, [unos_ID, up_time, mass])
                        except (PermissionError, OSError, IOError):
                            file_status = False

                    ts = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                    
                    if upload_status == True or file_status == True:
                        if measure == "km":
                            ts.place(relx= tsx, rely= 0.6, anchor= CENTER)
                        elif measure == "uo":
                            ts.place(relx= tsx, rely= 0.8, anchor= CENTER)
                    else:
                        pass

                    del m_arr[:]
                else:
                    pass

    #Functions necessary for user to commence a data acquisition option and, subsequently, for that option to collect data and 
    #upload to the database.
    def start_coll():
        global STOP
        STOP = False
        
        MT_thread = Thread(target= MT, args= (name[0], baud_rate[0], t_o[0]),)
        BT_thread = Thread(target= BT, args= (name[1], baud_rate[0], t_o[1]),)
        FT_1_thread = Thread(target= FT, args= (name[2], baud_rate[1], t_o[2], lap, "km"),)
        FT_2_thread = Thread(target= FT, args= (name[3], baud_rate[1], t_o[2], lap, "uo"),)

        MT_thread.start()
        BT_thread.start()
        FT_1_thread.start()
        FT_2_thread.start()

        halt = Button(disp_w, text= "Stop data collection", font= txt, padx= 10, command= lambda: q("data"))
        halt.place(relx= 0.5, rely= 0.1, anchor= CENTER)

        t_init = datetime.now() + timedelta(seconds= 5)
        t_end = t_init + timedelta(hours= 8)
        state = "Perfusion started at: {0}; stop at: {1}.".format(t_init.strftime("%H:%M:%S"),t_end.strftime("%H:%M:%S"))
        Label(disp_w, text= state, font= txt).place(relx= 0.5, rely= 0.2, anchor= CENTER)

        root.after(1000*perf_time, lambda: q("data"))

    def port_detect():
        global name
        global CHECK_AGAIN
        
        if OS == "Darwin":
            ports = serial.tools.list_ports.comports()
        elif OS == "Linux" or OS == "Windows":
            ports = sorted(serial.tools.list_ports.comports())

        if CHECK_AGAIN == False:
            for dev,descr,hwid in ports:
                    if dev.find("COM") != -1 or dev.find("USB") != -1 or dev.find("usbserial") != -1:
                        name.append(dev)
                    else:
                        pass

            Nusb = len(name)

            if Nusb != 4:
                if Nusb == 0:
                    Label(port_w, text= "No sensors connected.", font= txt, padx= prt_padx).place(relx= 0.5, rely= 0.85, anchor= CENTER)
                elif Nusb == 1:
                    Label(port_w, text= "Only 1 sensor is connected. Plug all in the correct order.", font= txt, padx= 15).place(relx= 0.5, rely= 0.85, anchor= CENTER)
                elif Nusb == 2 or Nusb == 3:
                    Label(port_w, text= "Only {} sensors are connected. Plug all in the correct order.".format(Nusb), font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
                else:
                    pass
                name = []

            elif Nusb == 4:
                Label(port_w, text= "Data collection ready to commence!", font= txt, padx= 100).place(relx= 0.5, rely= 0.85, anchor= CENTER)     
                CHECK_AGAIN = True

                def degunker(port_name, b, t):
                    with ser.Serial(port_name, baudrate= b, timeout= t) as degunk_port:
                        diff = 0
                        start = monotonic()
                        while diff < 10:
                            try:
                                if degunk_port.is_open == False:
                                    degunk_port.open()

                                BT_str = str(degunk_port.read(43))
                            except (OSError, FileNotFoundError):
                                degunk_port.close()
                                alert = sa.play_buffer(aud, 1, 2, N)
                            diff = monotonic() - start

                degunk_thread = Thread(target= degunker, args= (name[1], baud_rate[0], t_o[1]),)
                degunk_thread.start()
                degunk_thread.join()

                collecting = Button(disp_w, text= "Start data collection", font= txt, command= start_coll).place(relx= 0.5, rely= 0.1, anchor= CENTER)

        elif CHECK_AGAIN == True:
            Label(port_w, text= "Data collection ready to commence!", font= txt, padx= 100).place(relx= 0.5, rely= 0.85, anchor= CENTER)

    def choice():
        global CHOOSE_AGN
        global unos_ID
        global c_or_t
        
        def upload(instr):
            fn, intro_str, head_row, data_row = "", "", [], []

            if instr == "istat":
                head_row = ["UNOS_ID", "time_stamp", "side", "ph", "pco2", "po2", "be", "hco3", "tco2", "so2", "Na", "K", "Ca", "glu", "hct", "hb"]
                data_row = [unos_ID, iside_txt.get(), pH_txt.get(), PCO2_txt.get(), PO2_txt.get(), BE_txt.get(), HCO3_txt.get(), TCO2_istat_txt.get(), 
                            sO2_txt.get(), iNa_txt.get(), iK_txt.get(), iCa_txt.get(), iGlu_txt.get(), iHct_txt.get(), Hb_txt.get()]
            elif instr == "pic":
                head_row = ["UNOS_ID", "time_stamp", "side", "glu", "BUN", "Ca", "cre", "egfr", "alb", "Na", "K", "Cl", "tco2"]
                data_row = [unos_ID, pside_txt.get(), pGlu_txt.get(), BUN_txt.get(), pCa_txt.get(), Cre_txt.get(), eGFR_txt.get(), 
                            ALB_txt.get(), pNa_txt.get(), pK_txt.get(), Cl_txt.get(), TCO2_pic_txt.get()]
            elif instr == "meds":
                head_row = ["UNOS_ID", "time_stamp", "medication", "dosage"]
                data_row = [unos_ID, med_txt.get(), amt_txt.get()]
            elif instr == "perf":
                head_row = ["UNOS_ID", "time_stamp", "A1", "A2", "A3", "A4", "A5", "V1", "V2", "V3", "V4", "V5", "U1", "U2"]
                data_row = [unos_ID, A1_txt.get(), A2_txt.get(), A3_txt.get(), A4_txt.get(), A5_txt.get(), V1_txt.get(), 
                            V2_txt.get(), V3_txt.get(), V4_txt.get(), V5_txt.get(), U1_txt.get(), U2_txt.get()]
            elif instr == "biop":
                head_row = ["UNOS_ID", "time_stamp", "CFM1", "CFZ1", "CFM2", "CFZ2", "CFM3", "CFZ3", "CFM4", "CFZ4", "CFM5", "CFZ5", "MFM1", "MFZ1", 
                            "MFM2", "MFZ2", "MFM3", "MFZ3", "MFM4", "MFZ4", "MFM5", "MFZ5"]
                data_row = [unos_ID, CFM1_txt.get(), CFZ1_txt.get(), CFM2_txt.get(), CFZ2_txt.get(), CFM3_txt.get(), CFZ3_txt.get(), CFM4_txt.get(), 
                            CFZ4_txt.get(), CFM5_txt.get(), CFZ5_txt.get(), MFM1_txt.get(), MFZ1_txt.get(), MFM2_txt.get(), MFZ2_txt.get(), 
                            MFM3_txt.get(), MFZ3_txt.get(), MFM4_txt.get(), MFZ4_txt.get(), MFM5_txt.get(), MFZ5_txt.get()]

            upload_status,file_status = True,True
            
            if instr == "meds":
                fn = "{0}_{1}.csv".format(unos_ID, instr)
                intro_str = "INSERT INTO dbo.{}".format(instr)
            else:
                fn = "{0}_{1}_{2}.csv".format(unos_ID, c_or_t, instr)
                intro_str = "INSERT INTO dbo.{0}_{1}".format(instr, c_or_t)

            try:
                with pyodbc.connect(connString) as cnxn_bg:
                    with cnxn_bg.cursor() as cursor:
                        if instr == "istat":                                       
                            execstr_1 = "([{0}], [{1}], [{2}], [{3}], [{4}], [{5}], [{6}], [{7}], [{8}], [{9}], [{10}], [{11}]," 
                            execstr_2 =  " [{12}], [{13}], [{14}], [{15}]) VALUES('{16}', GETDATE(), '{17}', '{18}', '{19}', '{20}', '{21}', '{22}',"
                            execstr_3 =  " '{23}', '{24}', '{25}', '{26}', '{27}', '{28}', '{29}', '{30}');"
                            execstr = intro_str+execstr_1+execstr_2+execstr_3
                        elif instr == "pic":
                            execstr_1 = "([{0}], [{1}], [{2}], [{3}], [{4}], [{5}], [{6}], [{7}], [{8}], [{9}], [{10}], [{11}], [{12}])"
                            execstr_2 = " VALUES('{13}', GETDATE(), '{14}', '{15}', '{16}', '{17}', '{18}', '{19}', '{20}', '{21}', '{22}', '{23}', '{24}');"  
                            execstr = intro_str+execstr_1+execstr_2
                        elif instr == "meds":
                            execstr_1 = "([{0}], [{1}], [{2}], [{3}]) VALUES('{4}', GETDATE(), '{5}', '{6}');"
                            execstr = intro_str+execstr_1
                        elif instr == "perf":
                            execstr_1 = "([{0}], [{1}], [{2}], [{3}], [{4}], [{5}], [{6}], [{7}], [{8}], [{9}], [{10}], [{11}], [{12}], [{13}])"
                            execstr_2 = " VALUES('{14}', GETDATE(), '{15}', '{16}', '{17}', '{18}', '{19}', '{20}', '{21}', '{22}', '{23}', '{24}', '{25}', '{26}');"
                            execstr = intro_str+execstr_1+execstr_2
                            print(head_row, data_row)
                        elif instr == "biop":
                            execstr_1 = "([{0}], [{1}], [{2}], [{3}], [{4}], [{5}], [{6}], [{7}], [{8}], [{9}], [{10}], [{11}], [{12}],"
                            execstr_2 = " [{13}], [{14}], [{15}], [{16}], [{17}], [{18}], [{19}], [{20}], [{21}])"
                            execstr_3 = " VALUES('{22}', GETDATE(), '{23}', '{24}', '{25}', '{26}', '{27}', '{28}', '{29}', '{30}', '{31}', '{32}', '{33}',"
                            execstr_4 = " '{34}', '{35}', '{36}', '{37}', '{38}', '{39}', '{40}', '{41}', '{42}');"
                            execstr = intro_str+execstr_1+execstr_2+execstr_3+execstr_4
                        cursor.execute(execstr.format(*head_row, *data_row))
                        cnxn_bg.commit()
            except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                upload_status = False

            data_row.insert(1, datetime.utcnow())

            try:
                file_write(fn, head_row, data_row)
            except (PermissionError, OSError, IOError):
                file_status = False

            if upload_status == True or file_status == True:
                if instr == "istat":
                    Label(istat_w, text= "Data successfully saved!", font= txt, padx= 5).grid(row= 16, column= 2)
                elif instr == "pic":
                    Label(pic_w, text= "Data successfully saved!", font= txt, padx= 5).grid(row= 13, column= 4)
                elif instr == "meds":
                    Label(med_w, text= "Data\nsuccessfully saved!", font= txt, padx= 5).place(relx= 0.84, rely= med_yes, anchor= CENTER)
                elif instr == "perf":
                    Label(perf_w, text= "Data\nsuccessfully saved!", font= txt, padx= 5).grid(row= 16, column= 1)    
                elif instr == "biop":
                    Label(biop_w, text= "Data successfully saved!", font= txt, padx= 5).grid(row= 13, column= 3, columnspan= 2)
            else:
                if instr == "istat":
                    Label(istat_w, text= "Data saving unsuccessful.", font= txt).grid(row= 16, column= 2)
                elif instr == "pic":
                    Label(pic_w, text= "Data saving unsuccessful.", font= txt).grid(row= 13, column= 4)
                elif instr == "meds":
                    Label(med_w, text= "Data saving\nunsuccessful.", font= txt).place(relx= 0.84, rely= med_yes, anchor= CENTER)
                elif instr == "perf":
                    Label(perf_w, text= "Data\nsaving unsuccessful.", font= txt).grid(row= 16, column= 1)
                elif instr == "biop":
                    Label(biop_w, text= "Data saving unsuccessful.", font= txt).grid(row= 13, column= 3, columnspan= 2)

        if CHOOSE_AGN == False:
            if UNOS_AGAIN == "Y":
                unos_ID = unos_txt.get()
                c_or_t = exp_type.get()
            else:
                pass

            sel = var.get()

            if unos_ID == "" or c_or_t == "":
                Label(unos_w, text= "Incomplete information.", font= txt, padx= 30).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                      
                if sel == "":
                    Label(ch_w, text= "No selection made.", font= txt).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                else:
                    Label(ch_w, text= "Awaiting UNOS ID", font= txt).place(relx= 0.5, rely= 0.8, anchor= CENTER)
            elif unos_ID != "" and c_or_t != "":
                if UNOS_AGAIN == "Y":
                    Label(unos_w, text= "UNOS ID successfully entered.", font= txt).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                else:
                    Label(unos_w, text= "UNOS ID already set.", font= txt, padx= 60, pady= u_pady).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                    
                if sel == "":
                    Label(ch_w, text= "No selection made.", font= txt).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                else:
                    CHOOSE_AGN = True

                    #This section of code takes the UNOS ID, searches for the specific donor info pdf associated with that ID, 
                    #and generates a dataframe consisting of pertinent donor medical history data. The dataframe is displayed via
                    #GUI so that the user may edit any values that were incorrectly read from the PDF. When ready, the user can
                    #then upload this data to the Azure database.
                    if sel == "1":
                        Label(ch_w, text= "Donor information upload chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.8, anchor= CENTER)

                        def find(name, path):
                            for root, dirs, files in os.walk(path):
                                if name in files:
                                    return os.path.join(root, name)             
                                else:
                                    pass

                        def position_tracker(arr, length, idx= None):
                            pos = []

                            for i in range(length):
                                pos_p = []

                                if idx != None:
                                    for j in range(lt):
                                        if txt_arr[j].find(arr[i][idx]) != -1:
                                            pos_p.append(j) 

                                    pos.append(pos_p)
                                else:
                                    for j in range(lt):
                                        if txt_arr[j].find(arr[i]) != -1:
                                            pos.append(j)
                            return pos

                        def donor_upload(data):
                            don_row = [None]*58
                            upload_status, file_status = True, True
                            
                            try:
                                df = data.transpose()
                                
                                head_row = ["blood_type","UNOS_ID","match_ID","height","weight","age","bmi","gender","kdpi","eth_race","cause",
                                            "mech","circ","cold_time","dcd","card_ar","CPR","diabetes","cancer","hypert","CAD","GI_dis","smoker","etoh",            
                                            "iv_drug","BP_avg","HR_avg","BP_high","dur_high","BP_low","dur_low","wbc","rbc","hgb","hct","plt","Na","K","Cl",            
                                            "BUN","crea","glu","tbili","dbili","idbili","sgot","sgpt","aphos","prothr","ptt","l_biop","l_glom_per","l_type",            
                                            "l_glom","r_biop","r_glom_per","r_type","r_glom"]
                                
                                don_row = [df.iloc[1,0],df.iloc[1,1],df.iloc[1,2],df.iloc[1,3],df.iloc[1,4],df.iloc[1,5],df.iloc[1,6],
                                           df.iloc[1,7],df.iloc[1,8],df.iloc[1,9],df.iloc[1,10],df.iloc[1,11],df.iloc[1,12],df.iloc[1,13],
                                           df.iloc[1,14],df.iloc[1,15],df.iloc[1,16],df.iloc[1,17],df.iloc[1,18],df.iloc[1,19],
                                           df.iloc[1,20],df.iloc[1,21],df.iloc[1,22],df.iloc[1,23],df.iloc[1,24],df.iloc[1,25],
                                           df.iloc[1,26],df.iloc[1,27],df.iloc[1,28],df.iloc[1,29],df.iloc[1,30],df.iloc[1,31],
                                           df.iloc[1,32],df.iloc[1,33],df.iloc[1,34],df.iloc[1,35],df.iloc[1,36],df.iloc[1,37],
                                           df.iloc[1,38],df.iloc[1,39],df.iloc[1,40],df.iloc[1,41],df.iloc[1,42],df.iloc[1,43],
                                           df.iloc[1,44],df.iloc[1,45],df.iloc[1,46],df.iloc[1,47],df.iloc[1,48],df.iloc[1,49],
                                           df.iloc[1,50],df.iloc[1,51],df.iloc[1,52],df.iloc[1,53],df.iloc[1,54],df.iloc[1,55],
                                           df.iloc[1,56],df.iloc[1,57]] 
                                
                                for i in range(0,58):
                                    if isinstance(don_row[i], float):
                                        if np.isnan(don_row[i]):
                                            don_row[i] = None
                                try:
                                    with pyodbc.connect(connString) as cnxn_DI:
                                        with cnxn_DI.cursor() as cursor:                                
                                            exec_str_1 = "INSERT INTO dbo.organ([{0}],[{1}],[{2}],[{3}],[{4}],[{5}],[{6}],[{7}],[{8}],[{9}],"
                                            exec_str_2 = "[{10}],[{11}],[{12}],[{13}],[{14}],[{15}],[{16}],[{17}],[{18}],[{19}],[{20}],[{21}],[{22}],"
                                            exec_str_3 = "[{23}],[{24}],[{25}],[{26}],[{27}],[{28}],[{29}],[{30}],[{31}],[{32}],[{33}],[{34}],[{35}],[{36}],[{37}],"
                                            exec_str_4 = "[{38}],[{39}],[{40}],[{41}],[{42}],[{43}],[{44}],[{45}],[{46}],[{47}],[{48}],[{49}],[{50}],[{51}],[{52}],"
                                            exec_str_5 = "[{53}],[{54}],[{55}],[{56}],[{57}]) "
                                            exec_str_6 = "VALUES('{58}','{59}','{60}','{61}','{62}','{63}','{64}','{65}','{66}','{67}','{68}','{69}','{70}','{71}',"
                                            exec_str_7 = "'{72}','{73}','{74}','{75}','{76}','{77}','{78}','{79}','{80}','{81}','{82}','{83}','{84}','{85}','{86}','{87}',"
                                            exec_str_8 = "'{88}','{89}','{90}','{91}','{92}','{93}','{94}','{95}','{96}','{97}','{98}','{99}','{100}','{101}','{102}',"
                                            exec_str_9 = "'{103}','{104}','{105}','{106}','{107}','{108}','{109}','{110}','{111}','{112}','{113}','{114}','{115}');"
                                            execstr = exec_str_1+exec_str_2+exec_str_3+exec_str_4+exec_str_5+exec_str_6+exec_str_7+exec_str_8+exec_str_9
                                            cursor.execute(execstr.format(*head_row, *don_row))
                                            cnxn_DI.commit()       
                                except (pyodbc.InterfaceError, pyodbc.OperationalError, pyodbc.ProgrammingError, pyodbc.IntegrityError, pyodbc.DataError, pyodbc.NotSupportedError):
                                    upload_status = False
                            except (KeyError, IndexError, pd.errors.InvalidIndexError):
                                pass
                            
                            try:
                                file_write("{}_donor_info.csv".format(unos_ID), head_row, don_row)
                            except (PermissionError, OSError, IOError):
                                file_status = False
                                
                            if upload_status == True or file_status == True:
                                Label(data_w, text= "Data successfully saved!", font= txt, padx= 5).place(relx= don_yes, rely= 0.95, anchor= CENTER)
                            else:
                                Label(data_w, text= "Data saving unsuccessful.", font= txt, padx= 5).place(relx= don_yes, rely= 0.95, anchor= CENTER)

                        if no_fitz == False:
                            donor_file = find("{}.pdf".format(unos_ID), "/")
                            doc = fitz.open(donor_file)
                            text = ""
                            txt_arr = []

                            for page in doc: 
                                text = page.get_text()
                                temp = text.split("\n")
                                temp = temp[4:]

                                for i in temp:
                                    if i == " ":
                                        pass
                                    else:
                                        txt_arr.append(i)

                            param = [['Blood Type:','Donor Summary for ***** *****'], ['Donor ID: ','Printed on:'], ['Height: ','Date of birth: '], 
                                       ['Weight: ','Age: '], ['Age: ','Body Mass Index (BMI): '], ['Body Mass Index (BMI): ','Gender: '],
                                       ['Gender: ','KDPI:'], ['KDPI:','Ethnicity/race: '], ['Ethnicity/race: ', 'Cause of death: '],
                                       ['Cause of death: ','Mechanism of injury: '], ['Mechanism of injury: ','Circumstance of death: '],
                                       ['Circumstance of death: ', 'Admit date:'], ['Cold Ischemic Time:','OR Date:'],
                                       ['Donor meets DCD criteria: ','Cardiac arrest/downtime?: '], ['Cardiac arrest/downtime?: ','CPR administered?: '], 
                                       ['CPR administered?: ','Donor Highlights: '],['History of diabetes: ','History of cancer: '],
                                       ['History of cancer: ','History of hypertension: '], ['History of hypertension: ','History of coronary artery disease (CAD): '],          
                                       ['History of coronary artery disease (CAD): ','Previous gastrointestinal disease: '],
                                       ['Previous gastrointestinal disease: ', 'Chest trauma: '], 
                                       ['Cigarette use (>20 pack years) ever: ','Heavy alcohol use (2+ drinks/daily): '],
                                       ['Heavy alcohol use (2+ drinks/daily): ','I.V. drug usage: '],
                                       ['I.V. drug usage: ','According to the OPTN policy in effect on the date of referral'], 
                                       ['Average/Actual BP','Average heart rate (bpm)'],['Average heart rate (bpm)','High BP'],
                                       ['High BP','Duration at high (minutes)'],['Duration at high (minutes)','Low BP'], 
                                       ['Low BP','Duration at low (minutes)'], ['Duration at low (minutes)','Core Body Temp.'], 
                                       ['WBC (thous/mcL)','RBC (mill/mcL)'],['RBC (mill/mcL)','HgB (g/dL)'],['HgB (g/dL)','Hct (%)'], 
                                       ['Hct (%)','Plt (thous/mcL)'], ['Plt (thous/mcL)','Bands (%)'], ['Na (mEq/L)','K+ (mmol/L)'],
                                       ['K+ (mmol/L)','Cl (mmol/L)'], ['Cl (mmol/L)','CO2 (mmol/L)'],['BUN (mg/dL)','Creatinine (mg/dL))'], 
                                       ['Creatinine (mg/dL))','Glucose (mg/dL)'], ['Glucose (mg/dL)','Total Bilirubin (mg/dL)'],
                                       ['Total Bilirubin (mg/dL)','Direct Bilirubin (mg/dL)'], ['Direct Bilirubin (mg/dL)','Indirect Bilirubin (mg/dL)'],
                                       ['Indirect Bilirubin (mg/dL)','SGOT (AST) (u/L)'], ['SGOT (AST) (u/L)','SGPT (ALT) (u/L)',],
                                       ['SGPT (ALT) (u/L)','Alkaline phosphatase (u/L)'], ['Alkaline phosphatase (u/L)','GGT (u/L)'],
                                       ['Prothrombin (PT) (seconds)','INR'],['PTT (seconds)','Serum Amylase (u/L)']]

                            lr_par = ["Left kidney biopsy:","Right kidney biopsy:"]
                            ren_par = ["            % Glomerulosclerosis: ","            Biopsy type: ","            Glomeruli Count: "]

                            coords,ren_coord,data,trunc = [],[],[],[]
                            lt, lp = len(txt_arr), len(param)
                            pos_i, pos_f, pos_lr = position_tracker(param, lp, 0), position_tracker(param, lp, 1), position_tracker(lr_par, 2)

                            for i in range(lp):  
                                l_coords = len(pos_i[i])

                                for j in range(l_coords):
                                    a2o = [pos_i[i][j], pos_f[i][j]]
                                    coords.append(a2o)

                            for i in coords:
                                st, prm_l = None, None
                                wonky = ["Donor ID:", "Ethnicity/race: ", "Circumstance of death: ", "Donor meets DCD criteria: ", "Cardiac arrest/downtime?: "]
                                boo_1, boo_2 = True, True

                                for j in wonky:
                                    st = txt_arr[i[0]].find(j)

                                    if st != -1:
                                        prm_l = len(j)
                                        boo_1 = False
                                        break
                                    else:
                                        pass

                                if boo_1 == False:
                                    p_data = txt_arr[i[0]]

                                    if p_data.find(wonky[0]) != -1:
                                        data.append([p_data,[p_data]])
                                    else:
                                        data.append([p_data,[(p_data)[st+prm_l:]]])
                                else:
                                    prm = txt_arr[i[0]]
                                    p_data = txt_arr[(i[0]+1):i[1]]
                                    l_pd = len(p_data)

                                    if l_pd == 0:
                                        p_data = [""]

                                    for k in data:
                                        if prm == k[0]:
                                            k[1] += p_data
                                            boo_2 = False
                                            break

                                    if boo_2 == True:
                                        data.append([prm, p_data])

                            for i in pos_lr:
                                if txt_arr[i+1].find("YES") == -1: 
                                    data.append([txt_arr[i], ["NO"]])

                                    for j in ren_par:
                                        data.append([j, ["NA"]])
                                else:
                                    data.append([txt_arr[i], ["YES"]])

                                    for j in ren_par:
                                        J = txt_arr[i:].index(j)
                                        V = J+1

                                        if txt_arr[i+V].isnumeric():
                                            data.append([j,[txt_arr[i+V]]])
                                        elif txt_arr[i+V].find(ren_par[1]) != -1:
                                            data.append([j,["NA"]])
                                        elif txt_arr[i+V].find(ren_par[2]) != -1:
                                            data.append([j,["NA"]])
                                        elif txt_arr[i+V].find("Kidney Pump Values:") != -1:
                                            data.append([j,["NA"]])

                            for i in data:
                                if isinstance(i[1], list):
                                    while i[1].count("") != 0:
                                        i[1].remove("")

                                    if len(i[1]) == 0:
                                        i[1].append("NA")
                                        
                                if i[1][0].find("Donor ID: ") != -1:
                                    ids = i[1][0].split(" (")
                                    for j in ids:
                                        i_id = j.find(":") + 2
                                        f_id = j.find(")")
                                        trunc.append(j[i_id:f_id])
                                elif len(i[1]) == 1: 
                                    trunc.append((i[1])[0])
                                else:
                                    trunc.append(", ".join(i[1]))

                            df = pd.DataFrame(columns= [param[i][0] for i in range(0,2)]+["Match ID:"]+[param[i][0] for i in range(2,lp)]+[lr_par[0]]+[ren_par[i] for i in range(3)]+[lr_par[1]]+[ren_par[i] for i in range(3)])
                            df_length = len(df)

                            try:
                                df.loc[df_length] = trunc
                                df.index = ["Values"]

                            except ValueError:
                                Label(unos_w, text= "No file associated with such an ID.\nRestart and enter a valid ID\nor enter values manually.", font= txt).place(relx= 0.5, rely= 0.8, anchor= CENTER)

                            table = df.transpose().reset_index().rename(columns={"index":"Parameters"})
                            Label(data_w, text= "Click when ready to upload:", font= txt).place(relx= 0.01, rely= 0.95, anchor= W)
                            donor_w = Frame(data_w, width= don_x*w, height= don_y*h, bd= 2, relief= "sunken")
                            donor_w.grid(row= 0, column= 0, padx= 10, pady= 10)
                            donor_w.grid_propagate(False)
                            donor_info = Table(donor_w, dataframe= table, showstatusbar= True)
                            donor_info.textcolor = "RoyalBlue1"
                            donor_info.cellbackgr = "white"
                            donor_info.boxoutlinecolor = "black"
                            donor_info.show()
                            donor_ul = Button(data_w, text= "Upload", font= txt, command= lambda: donor_upload(table)).place(relx= don_up, rely= 0.95, anchor= CENTER)   
                        else:
                            Label(data_w, text= "PDF scanner currently unavailable.\nUpdate Python to 3.7 or higher.", font= txt).place(relx= 0.5, rely= 0.5, anchor= CENTER)

                    #This option allows one to manually input blood gas data from the iStat and Piccolo devices to the Azure database.
                    elif sel == "2":
                        av_opt = ["Arterial", "Venous"]
                        Label(ch_w, text= "Perfusate data upload chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                                           
                        istat_w = Frame(data_w, width= chemf_x*w, height= chemf_y*h, bd= 2, relief= "sunken")
                        istat_w.grid(row= 0,  column= 0, padx= 10, pady= 10)
                        istat_w.grid_propagate(False)
                        pic_w = Frame(data_w, width= chemf_x*w, height= chemf_y*h, bd= 2, relief= "sunken")
                        pic_w.grid(row= 0,  column= 1, padx= 10, pady= 10)
                        pic_w.grid_propagate(False)
                        med_w = Frame(data_w, width= 2*chemf_x*w, height= med_y*h, bd= 2, relief= "sunken")
                        med_w.grid(row= 1, column= 0, padx= 10, pady= 10, columnspan= 2)
                        med_w.grid_propagate(False)
   
                        #iStat
                        iside_txt, pH_txt, PCO2_txt, PO2_txt = StringVar(), StringVar(), StringVar(), StringVar()
                        BE_txt, HCO3_txt, TCO2_istat_txt, sO2_txt = StringVar(), StringVar(), StringVar(), StringVar()
                        iNa_txt, iK_txt, iCa_txt, iGlu_txt = StringVar(), StringVar(), StringVar(), StringVar()
                        iHct_txt, Hb_txt = StringVar(), StringVar()
                    
                        iside_txt.set("Arterial")
                        
                        Label(istat_w, text= "iStat Measurements:", font= header).grid(row= 0, column= 2)
                        Label(istat_w, text= "A/V: ", font= txt).grid(row= 1, column= 1, padx= av_label)
                        iside_e = OptionMenu(istat_w, iside_txt, *av_opt).grid(row= 1, column= 2, ipadx= opt_label)
                        Label(istat_w, text= "pH: ", font= txt).grid(row= 2, column= 1)
                        pH_e = Entry(istat_w, text= pH_txt, font= txt).grid(row= 2, column= 2)
                        Label(istat_w, text= "PCO2: ", font= txt).grid(row= 3, column= 1)
                        PCO2_e = Entry(istat_w, text= PCO2_txt, font= txt).grid(row= 3, column= 2)
                        Label(istat_w, text= "PO2: ", font= txt).grid(row= 4, column= 1)
                        PO2_e = Entry(istat_w, text= PO2_txt, font= txt).grid(row= 4, column= 2)
                        Label(istat_w, text= "BE: ", font= txt).grid(row= 5, column= 1)
                        BE_e = Entry(istat_w, text= BE_txt, font= txt).grid(row= 5, column= 2)
                        Label(istat_w, text= "HCO3: ", font= txt).grid(row= 6, column= 1)
                        HCO3_e = Entry(istat_w, text= HCO3_txt, font= txt).grid(row= 6, column= 2)
                        Label(istat_w, text= "TCO2: ", font= txt).grid(row= 7, column= 1)
                        TCO2_istat_e = Entry(istat_w, text= TCO2_istat_txt, font= txt).grid(row= 7, column= 2)
                        Label(istat_w, text= "sO2: ", font= txt).grid(row= 8, column= 1)
                        sO2_e = Entry(istat_w, text= sO2_txt, font= txt).grid(row= 8, column= 2)
                        Label(istat_w, text= "Na: ", font= txt).grid(row= 9, column= 1)
                        iNa_e = Entry(istat_w, text= iNa_txt, font= txt).grid(row= 9, column= 2)
                        Label(istat_w, text= "K: ", font= txt).grid(row= 10, column= 1)
                        iK_e = Entry(istat_w, text= iK_txt, font= txt).grid(row= 10, column= 2)
                        Label(istat_w, text= "Ca: ", font= txt).grid(row= 11, column= 1)
                        iCa_e = Entry(istat_w, text= iCa_txt, font= txt).grid(row= 11, column= 2)
                        Label(istat_w, text= "Glu: ", font= txt).grid(row= 12, column= 1)
                        iGlu_e = Entry(istat_w, text= iGlu_txt, font= txt).grid(row= 12, column= 2)
                        Label(istat_w, text= "Hct: ", font= txt).grid(row= 13, column= 1)
                        iHct_e = Entry(istat_w, text= iHct_txt, font= txt).grid(row= 13, column= 2)
                        Label(istat_w, text= "Hb: ", font= txt).grid(row= 14, column= 1)
                        Hb_e = Entry(istat_w, text= Hb_txt, font= txt).grid(row= 14, column= 2)
                        
                        #Piccolo
                        pside_txt, pGlu_txt, BUN_txt, pCa_txt = StringVar(), StringVar(), StringVar(), StringVar()
                        Cre_txt, eGFR_txt, ALB_txt, pNa_txt = StringVar(), StringVar(), StringVar(), StringVar()
                        pK_txt, Cl_txt, TCO2_pic_txt = StringVar(), StringVar(), StringVar()
                        
                        pside_txt.set("Arterial")

                        Label(pic_w, text= "Piccolo Measurements:", font= header).grid(row= 0, column= 4)
                        Label(pic_w, text= "A/V: ", font= txt).grid(row= 1, column= 3, padx= av_label)
                        pside_e = OptionMenu(pic_w, pside_txt, *av_opt).grid(row= 1, column= 4, ipadx= opt_label)
                        Label(pic_w, text= "Glu: ", font= txt).grid(row= 2, column= 3)
                        pGlu_e = Entry(pic_w, text= pGlu_txt, font= txt).grid(row= 2, column= 4)
                        Label(pic_w, text= "BUN: ", font= txt).grid(row= 3, column= 3)
                        BUN_e = Entry(pic_w, text= BUN_txt, font= txt).grid(row= 3, column= 4)
                        Label(pic_w, text= "Ca: ", font= txt).grid(row= 4, column= 3)
                        pCa_e = Entry(pic_w, text= pCa_txt, font= txt).grid(row= 4, column= 4)
                        Label(pic_w, text= "Cre: ", font= txt).grid(row= 5, column= 3)
                        Cre_e = Entry(pic_w, text= Cre_txt, font= txt).grid(row= 5, column= 4)
                        Label(pic_w, text= "eGFR: ", font= txt).grid(row= 6, column= 3)
                        eGFR_e = Entry(pic_w, text= eGFR_txt, font= txt).grid(row= 6, column= 4)
                        Label(pic_w, text= "ALB: ", font= txt).grid(row= 7, column= 3)
                        ALB_e = Entry(pic_w, text= ALB_txt, font= txt).grid(row= 7, column= 4)
                        Label(pic_w, text= "Na: ", font= txt).grid(row= 8, column= 3)
                        pNa_e = Entry(pic_w, text= pNa_txt, font= txt).grid(row= 8, column= 4)
                        Label(pic_w, text= "K: ", font= txt).grid(row= 9, column= 3)
                        pK_e = Entry(pic_w, text= pK_txt, font= txt).grid(row= 9, column= 4)
                        Label(pic_w, text= "Cl: ", font= txt).grid(row= 10, column= 3)
                        Cl_e = Entry(pic_w, text= Cl_txt, font= txt).grid(row= 10, column= 4)
                        Label(pic_w, text= "TCO2: ", font= txt).grid(row= 11, column= 3)
                        TCO2_pic_e = Entry(pic_w, text= TCO2_pic_txt, font= txt).grid(row= 11, column= 4)
                        
                        #Medications
                        med_txt, amt_txt = StringVar(), StringVar()
                        
                        Label(med_w, text= "Medication administered:", font= txt).place(relx= 0.01, rely= 0.2)
                        med_e = Entry(med_w, text= med_txt, font= txt).place(relx= 0.01, rely= 0.5)
                        Label(med_w, text= "Amount (in mL):", font= txt).place(relx= 0.35, rely= 0.2)
                        amt_e = Entry(med_w, text= amt_txt, font= txt).place(relx= 0.35, rely= 0.5)

                        submit_istat = Button(istat_w, text= "Submit", command= lambda: upload("istat"), font= txt).grid(row= 15, column= 2, pady= chemsub_pady)
                        submit_pic = Button(pic_w, text= "Submit", command= lambda: upload("pic"), font= txt).grid(row= 12, column= 4, pady= chemsub_pady)
                        submit_med = Button(med_w, text= "Submit", command= lambda: upload("meds"), font= txt).place(relx= sub_med, rely= 0.1)
                        
                    #This option collects data from the myriad perfusion sensors, integrates and formats the data, and then
                    #uploads it to the Azure database.
                    elif sel == "3":
                        global port_w
                        global disp_w                        
                        global vals
                        port_w = Frame(data_w, width= prt_x*w, height= prt_y*h, bd = 2, relief= "sunken")
                        port_w.grid(row= 0, column= 0, padx= 10, pady= 10)
                        port_w.grid_propagate(False)
                        disp_w = Frame(data_w, width= disp_x*w, height= disp_y*h, bd = 2, relief= "sunken")
                        disp_w.grid(row= 1, column= 0, padx= 10, pady= 10)
                        disp_w.grid_propagate(False)
                        vals = LabelFrame(disp_w, text= "Sensor Data Feed:", font= txt, bg= "white", width= val_x*w, height= val_y*h, bd= 2, relief= "groove")
                        vals.place(relx= 0.5, rely= 0.6, anchor= CENTER)
                        row1 = Label(vals, text= "Last Bioconsole update (time stamp):", font= txt, bg= "white")
                        row1.place(relx= 0.05, rely= 0.2, anchor= W) 
                        row2 = Label(vals, text= "Last Biotrend update (time stamp):", font= txt, bg= "white")
                        row2.place(relx= 0.05, rely= 0.4, anchor= W) 
                        row3 = Label(vals, text= "Last kidney weight update (time stamp):", font= txt, bg= "white")
                        row3.place(relx= 0.05, rely= 0.6, anchor= W) 
                        row4 = Label(vals, text= "Last urine output update (time stamp):", font= txt, bg= "white")
                        row4.place(relx= 0.05, rely= 0.8, anchor= W) 

                        Label(ch_w, text= "Sensor data collection chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                        user_guide_1 = "Plug in the devices in the following order:\n- Medtronic Bioconsole\n- Medtronic Biotrend\n- Force transducers (kidney scale, then urine scale)"
                        Label(port_w, text= user_guide_1, font= txt).place(relx= 0.5, rely= 0.3, anchor= CENTER)
                        port_check = Button(port_w, text= "Click to check port status", command= port_detect, font= txt).place(relx= 0.5, rely= 0.65, anchor= CENTER)
                    
                    #This option allows one to scan in samples for perfusate, urine, and biopsy collections.
                    elif sel == "4":
                        Label(ch_w, text= "Sample scanning chosen.", font= txt, padx= 30).place(relx= 0.5, rely= 0.8, anchor= CENTER)
                        perf_w = Frame(data_w, width= (chemf_x-0.1)*w, height= (chemf_y+0.15)*h, bd= 2, relief= "sunken")
                        perf_w.grid(row= 0,  column= 0, padx= 10, pady= 10)
                        perf_w.grid_propagate(False)
                        biop_w = Frame(data_w, width= (chemf_x+0.1)*w, height= (chemf_y+0.15)*h, bd= 2, relief= "sunken")
                        biop_w.grid(row= 0,  column= 1, padx= 10, pady= 10)
                        biop_w.grid_propagate(False)
                        
                        A1_txt, A2_txt, A3_txt, A4_txt, A5_txt = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
                        V1_txt, V2_txt, V3_txt, V4_txt, V5_txt = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
                        U1_txt, U2_txt = StringVar(), StringVar()
                        
                        #Arterial perfusates
                        Label(perf_w, text= "Arterial Perfusates:", font= txt).grid(row= 0, column= 1)
                        A1_e = Entry(perf_w, text= A1_txt, font= txt, width= 15).grid(row= 1, column= 1, padx= perf_pad)
                        A2_e = Entry(perf_w, text= A2_txt, font= txt, width= 15).grid(row= 2, column= 1)
                        A3_e = Entry(perf_w, text= A3_txt, font= txt, width= 15).grid(row= 3, column= 1)
                        A4_e = Entry(perf_w, text= A4_txt, font= txt, width= 15).grid(row= 4, column= 1)
                        A5_e = Entry(perf_w, text= A5_txt, font= txt, width= 15).grid(row= 5, column= 1)
                        
                        #Venous perfusates
                        Label(perf_w, text= "Venous Perfusates:", font= txt).grid(row= 6, column= 1)
                        V1_e = Entry(perf_w, text= V1_txt, font= txt, width= 15).grid(row= 7, column= 1)
                        V2_e = Entry(perf_w, text= V2_txt, font= txt, width= 15).grid(row= 8, column= 1)
                        V3_e = Entry(perf_w, text= V3_txt, font= txt, width= 15).grid(row= 9, column= 1)
                        V4_e = Entry(perf_w, text= V4_txt, font= txt, width= 15).grid(row= 10, column= 1)
                        V5_e = Entry(perf_w, text= V5_txt, font= txt, width= 15).grid(row= 11, column= 1)
                        
                        #Urine samples
                        Label(perf_w, text= "Urine Samples:", font= txt).grid(row= 12, column= 1)
                        U1_e = Entry(perf_w, text= U1_txt, font= txt, width= 15).grid(row= 13, column= 1)
                        U2_e = Entry(perf_w, text= U2_txt, font= txt, width= 15).grid(row= 14, column= 1)
                        
                        CFM1_txt, CFM2_txt, CFM3_txt, CFM4_txt, CFM5_txt = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
                        CFZ1_txt, CFZ2_txt, CFZ3_txt, CFZ4_txt, CFZ5_txt = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
                        MFM1_txt, MFM2_txt, MFM3_txt, MFM4_txt, MFM5_txt = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
                        MFZ1_txt, MFZ2_txt, MFZ3_txt, MFZ4_txt, MFZ5_txt = StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
                        
                        Label(biop_w, text= "Site 1:", font= txt).grid(row= 1, column= 2, padx= biop_pad)
                        Label(biop_w, text= "Site 2:", font= txt).grid(row= 2, column= 2)
                        Label(biop_w, text= "Site 3:", font= txt).grid(row= 3, column= 2)
                        Label(biop_w, text= "Site 4:", font= txt).grid(row= 4, column= 2)
                        Label(biop_w, text= "Site 5:", font= txt).grid(row= 5, column= 2)
                        Label(biop_w, text= "Site 1:", font= txt).grid(row= 7, column= 2)
                        Label(biop_w, text= "Site 2:", font= txt).grid(row= 8, column= 2)
                        Label(biop_w, text= "Site 3:", font= txt).grid(row= 9, column= 2)
                        Label(biop_w, text= "Site 4:", font= txt).grid(row= 10, column= 2)
                        Label(biop_w, text= "Site 5:", font= txt).grid(row= 11, column= 2)
                        
                        #Cortical Formalin
                        Label(biop_w, text= "Cortical Formalin:", font= txt).grid(row= 0, column= 3)
                        CFM1_e = Entry(biop_w, text= CFM1_txt, font= txt, width= 15).grid(row= 1, column= 3)
                        CFM2_e = Entry(biop_w, text= CFM2_txt, font= txt, width= 15).grid(row= 2, column= 3)
                        CFM3_e = Entry(biop_w, text= CFM3_txt, font= txt, width= 15).grid(row= 3, column= 3)
                        CFM4_e = Entry(biop_w, text= CFM4_txt, font= txt, width= 15).grid(row= 4, column= 3)
                        CFM5_e = Entry(biop_w, text= CFM5_txt, font= txt, width= 15).grid(row= 5, column= 3)
                        
                        #Cortical Snap Frozen
                        Label(biop_w, text= "Cortical Frozen:", font= txt).grid(row= 6, column= 3)
                        CFZ1_e = Entry(biop_w, text= CFZ1_txt, font= txt, width= 15).grid(row= 7, column= 3)
                        CFZ2_e = Entry(biop_w, text= CFZ2_txt, font= txt, width= 15).grid(row= 8, column= 3)
                        CFZ3_e = Entry(biop_w, text= CFZ3_txt, font= txt, width= 15).grid(row= 9, column= 3)
                        CFZ4_e = Entry(biop_w, text= CFZ4_txt, font= txt, width= 15).grid(row= 10, column= 3)
                        CFZ5_e = Entry(biop_w, text= CFZ5_txt, font= txt, width= 15).grid(row= 11, column= 3)
                        
                        #Medullary Formalin
                        Label(biop_w, text= "Medullary Formalin:", font= txt).grid(row= 0, column= 4)
                        MFM1_e = Entry(biop_w, text= MFM1_txt, font= txt, width= 15).grid(row= 1, column= 4)
                        MFM2_e = Entry(biop_w, text= MFM2_txt, font= txt, width= 15).grid(row= 2, column= 4)
                        MFM3_e = Entry(biop_w, text= MFM3_txt, font= txt, width= 15).grid(row= 3, column= 4)
                        MFM4_e = Entry(biop_w, text= MFM4_txt, font= txt, width= 15).grid(row= 4, column= 4)
                        MFM5_e = Entry(biop_w, text= MFM5_txt, font= txt, width= 15).grid(row= 5, column= 4)
                        
                        #Medullary Snap Frozen
                        Label(biop_w, text= "Medullary Frozen:", font= txt).grid(row= 6, column= 4)
                        MFZ1_e = Entry(biop_w, text= MFZ1_txt, font= txt, width= 15).grid(row= 7, column= 4)
                        MFZ2_e = Entry(biop_w, text= MFZ2_txt, font= txt, width= 15).grid(row= 8, column= 4)
                        MFZ3_e = Entry(biop_w, text= MFZ3_txt, font= txt, width= 15).grid(row= 9, column= 4)
                        MFZ4_e = Entry(biop_w, text= MFZ4_txt, font= txt, width= 15).grid(row= 10, column= 4)
                        MFZ5_e = Entry(biop_w, text= MFZ5_txt, font= txt, width= 15).grid(row= 11, column= 4)
                        
                        submit_perf = Button(perf_w, text= "Submit", command= lambda: upload("perf"), font= txt).grid(row= 15, column= 1, pady= chemsub_pady)
                        submit_biop = Button(biop_w, text= "Submit", command= lambda: upload("biop"), font= txt).grid(row= 12, column= 3, pady= chemsub_pady, columnspan= 2)
        else:
            Label(ch_w, text= "Selection already made.\nRestart to choose a new option.", font= txt, padx= allset_pad).place(relx= 0.5, rely= 0.8, anchor= CENTER)
            Label(unos_w, text= "UNOS ID already set.", font= txt, padx= 60, pady= u_pady).place(relx= 0.5, rely= 0.8, anchor= CENTER)

    #Now that the GUI has been initialized and all the functions ready for execution, the block of code below establishes the widgets necessary
    #for the user to interact with the program.
    opts_w = LabelFrame(root, text= "Settings:", width= of_x*w, height= of_y*h, bd= 2, relief= "raised", font= header)
    opts_w.grid(row= 0, column= 0, padx= 10, pady= 10)
    opts_w.grid_propagate(False)
    data_w = LabelFrame(root, text= "Data Output:", width= df_x*w, height= df_y*h, bd= 2, relief= "raised", font= header)
    data_w.grid(row= 0, column= 1, padx= 10, pady= 10)
    data_w.grid_propagate(False)

    ch_w = Frame(opts_w, bd = 2, width= cf_x*w, height= cf_y*h, relief= "sunken")
    ch_w.grid(row= 0, column= 0, columnspan= 3, padx= 10, pady= 10)
    ch_w.grid_propagate(False)
    unos_w = Frame(opts_w, bd = 2, width= uf_x*w, height= uf_y*h, relief= "sunken")
    unos_w.grid(row= 1, column= 0, columnspan= 3, padx= 10, pady= 10)
    unos_w.grid_propagate(False)

    Label(ch_w, text= "Select which of the below\nthat you would like to do:", font= txt).place(relx= 0.5, rely= 0.15, anchor= CENTER)
    R1 = Radiobutton(ch_w, text= "Donor information upload", font= txt, variable= var, value= "1")
    R1.place(relx= radx, rely= 0.3, anchor= W)
    R2 = Radiobutton(ch_w, text= "Perfusate data and medications", font= txt, variable= var, value= "2")
    R2.place(relx= radx, rely= 0.4, anchor= W)
    R3 = Radiobutton(ch_w, text= "Sensor data collection", font= txt, variable= var, value= "3")
    R3.place(relx= radx, rely= 0.5, anchor= W)
    R4 = Radiobutton(ch_w, text= "Samples", font= txt, variable= var, value= "4")
    R4.place(relx= radx, rely= 0.6, anchor= W)

    Label(unos_w, text= "Enter UNOS ID (case sensitive):", font= txt).place(relx= 0.5, rely= 0.15, anchor= CENTER)
    unos = Entry(unos_w, text= unos_txt, font= txt)
    unos.place(relx= 0.5, rely= 0.35, anchor= CENTER)
    C = Radiobutton(unos_w, text= "Control", font= txt, variable= exp_type, value= "c")
    C.place(relx= 0.35, rely= 0.5, anchor= W)
    E = Radiobutton(unos_w, text= "Experimental", font= txt, variable= exp_type, value= "t")
    E.place(relx= 0.35, rely= 0.6, anchor= W)
    
    submit = Button(opts_w, text= "Submit", font= txt, command= choice).grid(row= 2, column= 0, pady= 5, ipadx= sub_pad)
    restart = Button (opts_w, text= "Restart", font= txt, command= anew).grid(row= 2,column= 1, pady= 5, ipadx= rest_pad)
    exit = Button(opts_w, text= "Exit", font= txt, command= lambda: q("set")).grid(row= 2, column= 2, pady= 5, ipadx= ex_pad)

    root.mainloop()
    
app("Y")
