import serial as ser, numpy as np, simpleaudio as sa, pandas as pd
import pyodbc, serial.tools.list_ports, os, sys, platform
from time import monotonic, sleep
from datetime import datetime, timedelta
from tkinter import *
from threading import Thread
from pandastable import Table

#fitz (the name for the PyMuPDF library) only works on Python 3.7 or higher. For the programs running on the Raspberry Pi devices, the Python version
#is less than 3.7. This code allows one to retain the fitz module for the Windows .exe file while ignoring said module for the program on Raspberry Pi.
no_fitz = False

try:
    import fitz
except ImportError:
    no_fitz = True

#The block of code below sets up the initial screen/GUI for the app. The program was originally designed for an 800x480 Raspberry Pi and tested 
#on a 1440x900 MacBook so those are the standards for initializing the GUI screen size.
root = Tk()
root.title("Kidney Perfusion App")
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
don_x,don_y = 0.59, 0.8
chemf_x,chemf_y = 0.255, 0.85
prt_x,prt_y = 0.54, 0.29
prt_padx = 100
disp_x,disp_y = 0.54, 0.53
val_x,val_y = 0.45, 0.35
tsx = 0.85
chemsub_pady = 10
istat_relx,pic_relx = 0.5, 0.5
istat_rely,pic_rely = 0.6, 0.9 
allset_pad = 10
u_pady, sub_pad,rest_pad,ex_pad = 10, 1, 1, 5
file = os.path.abspath(__file__)
OS = platform.system()

if w >= 1440 and h >= 900:
    head_sz, txt_sz = 25, 20
    of_x,of_y = 0.36, 0.95
    df_x,df_y = 0.61, 0.95
    cf_x,cf_y = 0.34, 0.42
    radx = 0.25
    uf_x,uf_y = 0.34, 0.38
    don_x,don_y = 0.59, 0.8
    chemf_x,chemf_y = 0.29, 0.87
    prt_x,prt_y = 0.59, 0.25
    prt_padx = 150
    disp_x,disp_y = 0.59, 0.6
    val_x,val_y = 0.5, 0.4
    tsx = 0.75
    chemsub_pady = 30
    istat_relx,pic_relx = 0.48, 0.525
    istat_rely,pic_rely = 0.55, 0.8
    allset_pad = 45
    u_pady, sub_pad,rest_pad,ex_pad = 25, 5, 5, 15

var,unos_txt = StringVar(), StringVar()
lap, perf_time, name, baud_rate, t_o = 5, 30000, [], [9600,2400], [5.1, 5.2, 0.2]
CHOOSE_AGN, CHECK_AGAIN, ST_AGN, STOP = False, False, False, False
null_input, nan, connString, compl = "b\'\'", float("nan"), None, 0

#The code below establishes the necessary information to interact with the given OS. Note: although the GUI was designed on a Mac, 
#the full software does not function on Mac.
if OS == "Linux":
    rest_comm = "python3 {}".format(file)
    
    dsn = "DTKserverdatasource"
    user = "dtk_lab@dtk-server"
    password = "data-collection1"
    database = "perf-data"
    connString = "DSN={0};UID={1};PWD={2};DATABASE={3};".format(dsn,user,password,database)
    
elif OS == "Windows":
    rest_comm = "start {}".format(file)
    
    driver = "{SQL Server}"
    server = "dtk-server.database.windows.net"
    database = "perf-data"
    username = "dtk_lab"
    password = "data-collection1"
    connString = "DRIVER={0};SERVER={1};DATABASE={2};UID={3};PWD={4}".format(driver,server,database,username,password)

header,txt = ("Helvetica", head_sz, "bold"), ("Helvetica", txt_sz)    

#This initializes the warning sound to be played if a sensor falls asleep.
N = 44100
T = 0.25
x = np.linspace(0, T*N,  N, False)
aud = np.sin(600 * x * 2 * np.pi)
aud *= 32767/np.max(np.abs(aud))
aud = aud.astype(np.int16)

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
    global STOP
    STOP = True
    os.system(rest_comm)
    root.destroy()
    
def q(tipo):
    global STOP
    STOP = True
    
    if tipo == "data":
        Label(disp_w, text= "Data collection complete. Goodbye!", font= txt, padx= 100).place(relx= 0.5, rely= 0.2, anchor= CENTER)
    elif tipo == "pause":
        Label(disp_w, text= "Data collection stopped.", font= txt, padx= 100).place(relx= 0.5, rely= 0.2, anchor= CENTER)
        global compl
        compl = monotonic() - perf_st
        coll_agn = Button(disp_w, text= "Restart Data Collection", font= txt, command= start_coll, padx= 10).place(relx= 0.5, rely= 0.1, anchor= CENTER)
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

#This function parses the data output from the Biotrend device to retreive the venous sO2 and the hematocrit during perfusion. Due to the 
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
    with pyodbc.connect(connString) as cnxn_MT:
        with cnxn_MT.cursor() as cursor:
            with ser.Serial(port_name, baudrate= b, timeout= t) as MT_port:                                              
                MT_port.write(b"DR 05 013B\r")

                while STOP == False:
                    try:
                        if MT_port.is_open == False:
                            MT_port.open()

                        MT_str = str(MT_port.read(35))
                        if MT_str == null_input:
                            alert()
                            execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                            cursor.execute(execstr)
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

                                execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure], [rpm]) VALUES('{}', GETDATE(), {}, {}, {});".format(unos_ID, data_AF, data_AP, rpm)
                                cursor.execute(execstr)
                            except (IndexError, ValueError, TypeError):
                                alert()
                                execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                                cursor.execute(execstr)
                    except (OSError, FileNotFoundError):
                        MT_port.close()
                        alert()
                        sleep(5)
                        execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                        cursor.execute(execstr)
                    cnxn_MT.commit()
                    ts_MT = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                    ts_MT.place(relx= tsx, rely= 0.2, anchor= CENTER) 

#Medtronic Biotrend sensor function                                                  
def BT(port_name, b, t):
    with pyodbc.connect(connString) as cnxn_BT:
        with cnxn_BT.cursor() as cursor:
            with ser.Serial(port_name, baudrate= b, timeout= t) as BT_port:                            
                while STOP == False:
                    try:
                        if BT_port.is_open == False:
                            BT_port.open()

                        BT_str = str(BT_port.read(43))
                        data_sO2v, data_hct = data_check(BT_str)

                        if np.isnan(data_sO2v) and np.isnan(data_hct):
                            execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                            cursor.execute(execstr)
                        elif np.isnan(data_sO2v) == True and np.isnan(data_hct) == False:
                            execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [hct]) VALUES('{}', GETDATE(), {});".format(unos_ID, data_hct)
                            cursor.execute(execstr)
                        elif np.isnan(data_sO2v) == False and np.isnan(data_hct) == True:
                            execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2]) VALUES('{}', GETDATE(), {});".format(unos_ID, data_sO2v)
                            cursor.execute(execstr)
                        else:
                            execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{}', GETDATE(), {}, {});".format(unos_ID, data_sO2v, data_hct)
                            cursor.execute(execstr)
                    except (OSError, FileNotFoundError):
                        BT_port.close()
                        alert()
                        sleep(5)
                        execstr = "INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                        cursor.execute(execstr)
                    cnxn_BT.commit()
                    ts_BT = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                    ts_BT.place(relx= tsx, rely= 0.4, anchor= CENTER) 

#Force transducer sensor function. The force transducer outputs rate at a frequency of 10 Hz. The "interval" parameter allows us to set at 
#what time interval at which we want to collect data (i.e. every x seconds). The function collects the data point closest to the "x"
#interval mark.
def FT(port_name, b, t, interval, measure):
        with pyodbc.connect(connString) as cnxn_FT:
                with cnxn_FT.cursor() as cursor:
                        with ser.Serial(port_name, baudrate= b, timeout= t) as FT_port:
                            rd, check, mass, m_arr = 0, 0, 0, []
                            start = monotonic()

                            while STOP == False:                                            
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

                                    if measure == "km":
                                        if sleepy:
                                            alert()
                                            execstr = "INSERT INTO dbo.km_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                                            cursor.execute(execstr)
                                        else:
                                            execstr = "INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{}', GETDATE(), {});".format(unos_ID, mass)
                                            cursor.execute(execstr)
                                        ts_km = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                                        ts_km.place(relx= tsx, rely= 0.6, anchor= CENTER) 
                                    elif measure == "uo":
                                        if sleepy:
                                            alert()
                                            execstr = "INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                                            cursor.execute(execstr)
                                        else:
                                            execstr = "INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp], [urine_output]) VALUES('{}', GETDATE(), {});".format(unos_ID, mass)
                                            cursor.execute(execstr)
                                        ts_uo = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                                        ts_uo.place(relx= tsx, rely= 0.8, anchor= CENTER) 
                                    cnxn_FT.commit()
                                    del m_arr[:]
                                else:
                                    pass

#Functions necessary for user to commence a data acquisition option and, subsequently, for that option to collect data and 
#upload to the database.
def start_coll():
    STOP = False
    
    MT_thread = Thread(target= MT, args= (name[0], baud_rate[0], t_o[0]),)
    BT_thread = Thread(target= BT, args= (name[1], baud_rate[0], t_o[1]),)
    FT_1_thread = Thread(target= FT, args= (name[2], baud_rate[1], t_o[2], lap, "km"),)
    FT_2_thread = Thread(target= FT, args= (name[3], baud_rate[1], t_o[2], lap, "uo"),)

    MT_thread.start()
    BT_thread.start()
    FT_1_thread.start()
    FT_2_thread.start()
    
    halt = Button(disp_w, text= "Stop Data Collection", font= txt, padx= 20, command= lambda: q("pause"))
    halt.place(relx= 0.5, rely= 0.1, anchor= CENTER)

    if ST_AGN == False:
        t_init = datetime.now() + timedelta(seconds= 5)
        t_end = t_init + timedelta(hours= 8)
        global perf_st
        perf_st = monotonic()
        Label(disp_w, text= "Perfusion started at: {0}; stop at: {1}.".format(t_init.strftime("%H:%M:%S"),t_end.strftime("%H:%M:%S")), font= txt).place(relx= 0.5, rely= 0.2, anchor= CENTER)
    
    global ST_AGN
    ST_AGN = True
    root.after(1000*(perf_time-compl), lambda: q("data"))

def port_detect():
    global name
    global CHECK_AGAIN
    ports = serial.tools.list_ports.comports()
    
    for dev,descr,hwid in sorted(ports):
            if dev.find("COM") != -1 or dev.find("USB") != -1 or dev.find("usbserial") != -1:
                name.append(dev)
            else:
                pass
    
    Nusb = len(name)

    if Nusb != 4:
        if Nusb == 0:
            Label(port_w, text= "No sensors connected.", font= txt, padx= prt_padx).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 1:
            Label(port_w, text= "Only 1 sensor is connected. Plug all in the correct order.", font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 2 or Nusb == 3:
            Label(port_w, text= "Only {} sensors are connected. Plug all in the correct order.".format(Nusb), font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        else:
            pass
        name = []
        
    elif Nusb == 4 and CHECK_AGAIN == False:
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

        collecting = Button(disp_w, text= "Start Data Collection", font= txt, command= start_coll).place(relx= 0.5, rely= 0.1, anchor= CENTER)
    
    elif Nusb == 4 and CHECK_AGAIN == True:
        Label(port_w, text= "Data collection ready to commence!", font= txt, padx= 100).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        
def choice():
    global CHOOSE_AGN
    global unos_ID
    
    if CHOOSE_AGN == False:
        unos_ID = unos_txt.get()
        sel = var.get()

        if unos_ID == "":
            Label(unos_w, text= "Blank UNOS ID entered.", font= txt, padx= 30).place(relx= 0.5, rely= 0.6, anchor= CENTER)
            
            if sel == "":
                Label(ch_w, text= "No selection made.", font= txt).place(relx= 0.5, rely= 0.7, anchor= CENTER)
            else:
                Label(ch_w, text= "Awaiting UNOS ID", font= txt).place(relx= 0.5, rely= 0.7, anchor= CENTER)
        elif unos_ID != "":
            Label(unos_w, text= "UNOS ID successfully entered.", font= txt).place(relx= 0.5, rely= 0.6, anchor= CENTER)
            
            if sel == "":
                Label(ch_w, text= "No selection made.", font= txt).place(relx= 0.5, rely= 0.7, anchor= CENTER)
            else:
                CHOOSE_AGN = True
                
                #This section of code takes the UNOS ID, searches for the specific donor info pdf associated with that ID, 
                #and generates a dataframe consisting of pertinent donor medical history data. The dataframe is displayed via
                #GUI so that the user may edit any values that were incorrectly read from the PDF. When ready, the user can
                #then upload this data to the Azure database.
                if sel == "1":
                    with pyodbc.connect(connString) as cnxn_DI:
                        with cnxn_DI.cursor() as cursor:
                            Label(ch_w, text= "Donor information upload chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.7, anchor= CENTER)

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
                                try:
                                    df = data.transpose()
                                    cnxn_str_1 = "INSERT INTO dbo.organ_t([blood_type],[ID],[height],[weight],[age],[bmi],[gender],[kdpi],[eth_race],[cause],"
                                    cnxn_str_2 = "[mech],[circ],[cold_time],[dcd],[card_ar],[CPR],[diabetes],[cancer],[hypert],[CAD],[GI_dis],[smoker],[etoh],"
                                    cnxn_str_3 = "[iv_drug],[BP_avg],[HR_avg],[BP_high],[dur_high],[BP_low],[dur_low],[wbc],[rbc],[hgb],[hct],[plt],[Na],[K],[Cl],"
                                    cnxn_str_4 = "[BUN],[crea],[glu],[tbili],[dbili],[idbili],[sgot],[sgpt],[aphos],[prothr],[ptt],[l_biop],[l_glom_per],[l_type],"
                                    cnxn_str_5 = "[l_glom],[r_biop],[r_glom_per],[r_type],[r_glom]) "
                                    cnxn_str_6 = "VALUES({0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20},{21},{22},"
                                    cnxn_str_7 = "{23},{24},{25},{26},{27},{28},{29},{30},{31},{32},{33},{34},{35},{36},{37},{38},{39},{40},{41},{42},{43},{44},"
                                    cnxn_str_8 = "{45},{46},{47},{48},{49},{50},{51},{52},{53},{54},{55},{56});"
                                    cnxn_str = cnxn_str_1+cnxn_str_2+cnxn_str_3+cnxn_str_4+cnxn_str_5+cnxn_str_6+cnxn_str_7+cnxn_str_8
                                    cursor.execute(cnxn_str.format(df.iloc[1,0],df.iloc[1,1],df.iloc[1,2],df.iloc[1,3],df.iloc[1,4],df.iloc[1,5],df.iloc[1,6],
                                                                   df.iloc[1,7],df.iloc[1,8],df.iloc[1,9],df.iloc[1,10],df.iloc[1,11],df.iloc[1,12],df.iloc[1,13],
                                                                   df.iloc[1,14],df.iloc[1,15],df.iloc[1,16],df.iloc[1,17],df.iloc[1,18],df.iloc[1,19],
                                                                   df.iloc[1,20],df.iloc[1,21],df.iloc[1,22],df.iloc[1,23],df.iloc[1,24],df.iloc[1,25],
                                                                   df.iloc[1,26],df.iloc[1,27],df.iloc[1,28],df.iloc[1,29],df.iloc[1,30],df.iloc[1,31],
                                                                   df.iloc[1,32],df.iloc[1,33],df.iloc[1,34],df.iloc[1,35],df.iloc[1,36],df.iloc[1,37],
                                                                   df.iloc[1,38],df.iloc[1,39],df.iloc[1,40],df.iloc[1,41],df.iloc[1,42],df.iloc[1,43],
                                                                   df.iloc[1,44],df.iloc[1,45],df.iloc[1,46],df.iloc[1,47],df.iloc[1,48],df.iloc[1,49],
                                                                   df.iloc[1,50],df.iloc[1,51],df.iloc[1,52],df.iloc[1,53],df.iloc[1,54],df.iloc[1,55],
                                                                   df.iloc[1,56]))
                                    cnxn_DI.commit()
                                    
                                except (KeyError, IndexError, pyodbc.ProgrammingError, pd.errors.InvalidIndexError):
                                    pass
                            
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

                                    if len(i[1]) == 1: 
                                        trunc.append((i[1])[0])
                                    else:
                                        trunc.append(", ".join(i[1]))


                                df = pd.DataFrame(columns= [param[i][0] for i in range(lp)]+[lr_par[0]]+[ren_par[i] for i in range(3)]+[lr_par[1]]+[ren_par[i] for i in range(3)])
                                df_length = len(df)

                                try:
                                    df.loc[df_length] = trunc
                                    df.index = ["Values"]

                                except ValueError:
                                    Label(unos_w, text= "No file associated with such an ID.\nRestart and enter a valid ID\nor enter values manually.", font= txt).place(relx= 0.5, rely= 0.6, anchor= CENTER)

                                table = df.transpose().reset_index().rename(columns={"index":"Parameters"})
                                Label(data_w, text= "Click submit when ready to upload:", font= txt).place(relx= 0.4, rely= 0.95, anchor= CENTER)
                                donor_w = Frame(data_w, width= don_x*w, height= don_y*h, bd= 2, relief= "sunken")
                                donor_w.grid(row= 0, column= 0, padx= 10, pady= 10)
                                donor_w.grid_propagate(False)
                                donor_info = Table(donor_w, dataframe= table, showstatusbar= True)
                                donor_info.textcolor = "RoyalBlue1"
                                donor_info.cellbackgr = "white"
                                donor_info.boxoutlinecolor = "black"
                                donor_info.show()
                                donor_ul = Button(data_w, text= "Upload", font= txt, command= lambda: donor_upload(table)).place(relx= 0.65, rely= 0.95, anchor= CENTER)   
                            else:
                                Label(data_w, text= "PDF scanner currently unavailable.\nUpdate Python to 3.7 or higher.", font= txt).place(relx= 0.5, rely= 0.5, anchor= CENTER)
                            
                #This option allows one to manually input blood gas data from the iStat and Piccolo devices to the Azure database.
                elif sel == "2":
                    Label(ch_w, text= "Blood gas data upload chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.7, anchor= CENTER)

                    istat_w = Frame(data_w, width= chemf_x*w, height= chemf_y*h, bd= 2, relief= "sunken")
                    istat_w.grid(row= 0,  column= 0, padx= 10, pady= 10)
                    istat_w.grid_propagate(False)
                    pic_w = Frame(data_w, width= chemf_x*w, height= chemf_y*h, bd= 2, relief= "sunken")
                    pic_w.grid(row= 0,  column= 1, padx= 10, pady= 10)
                    pic_w.grid_propagate(False)

                    def upload(instr):
                        with pyodbc.connect(connString) as cnxn_bg:
                            with cnxn_bg.cursor() as cursor:
                                if instr == "istat":
                                    try:  
                                        pH, PCO2, PO2 = float(pH_txt.get()), float(PCO2_txt.get()), float(PO2_txt.get())
                                        TCO2_istat, HCO3, BE = float(TCO2_istat_txt.get()), float(HCO3_txt.get()), float(BE_txt.get())
                                        sO2, Hb = float(sO2_txt.get()), float(Hb_txt.get())
                                        execstr = "INSERT INTO dbo.istat_t([UNOS_ID], [time_stamp], [ph], [pco2], [po2], [tco2], [hco3], [be], [so2], [hb]) VALUES('{}', GETDATE(), {}, {}, {}, {}, {}, {}, {}, {});".format(unos_ID, pH, PCO2, PO2, TCO2_istat, HCO3, BE, sO2, Hb)
                                        cursor.execute(execstr)
                                        cnxn_bg.commit()
                                        Label(istat_w, text= "Data successfully uploaded!", font= txt, padx= allset_pad).place(relx= istat_relx, rely= istat_rely, anchor= CENTER)
                                    except ValueError:
                                        Label(istat_w, text= "Invalid data type or blank entry", font= txt).place(relx= istat_relx, rely= istat_rely, anchor= CENTER) 
                                
                                elif instr == "pic":
                                    try:
                                        Na, K, TCO2_pic = float(Na_txt.get()), float(K_txt.get()), float(TCO2_pic_txt.get())
                                        Cl, Glu, Ca = float(Cl_txt.get()), float(Glu_txt.get()), float(Ca_txt.get())
                                        BUN, Cre, eGFR = float(BUN_txt.get()), float(Cre_txt.get()), float(eGFR_txt.get())
                                        ALP, AST, TBIL = float(ALP_txt.get()), float(AST_txt.get()), float(TBIL_txt.get())
                                        ALB, TP = float(ALB_txt.get()), float(TP_txt.get())
                                        execstr = "INSERT INTO dbo.pic_t([UNOS_ID], [time_stamp], [Na], [K], [tco2], [Cl], [glu], [Ca], [BUN], [cre], [egfr], [alp], [ast], [tbil], [alb], [tp]) VALUES('{}', GETDATE(), {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});".format(unos_ID, Na, K, TCO2_pic, Cl, Glu, Ca, BUN, Cre, eGFR, ALP, AST, TBIL, ALB, TP) 
                                        cursor.execute(execstr)
                                        cnxn_bg.commit()   
                                        Label(pic_w, text= "Data successfully uploaded!", font= txt, padx= allset_pad).place(relx= pic_relx, rely= pic_rely, anchor= CENTER)     
                                    except ValueError:
                                        Label(pic_w, text= "Invalid data type or blank entry.", font= txt).place(relx= pic_relx, rely= pic_rely, anchor= CENTER)

                    #iStat
                    pH_txt, PCO2_txt, PO2_txt, TCO2_istat_txt = StringVar(), StringVar(), StringVar(), StringVar()
                    HCO3_txt, BE_txt, sO2_txt, Hb_txt = StringVar(), StringVar(), StringVar(), StringVar()

                    Label(istat_w, text= "iStat Measurements:", font= header).grid(row= 0, column= 2)
                    Label(istat_w, text= "pH: ", font= txt).grid(row= 1, column= 1)
                    pH_e = Entry(istat_w, text= pH_txt, font= txt).grid(row= 1, column= 2)
                    Label(istat_w, text= "PCO2: ", font= txt).grid(row= 2, column= 1)
                    PCO2_e = Entry(istat_w, text= PCO2_txt, font= txt).grid(row= 2, column= 2)
                    Label(istat_w, text= "PO2: ", font= txt).grid(row= 3, column= 1)
                    PO2_e = Entry(istat_w, text= PO2_txt, font= txt).grid(row= 3, column= 2)
                    Label(istat_w, text= "TCO2: ", font= txt).grid(row= 4, column= 1)
                    TCO2_istat_e = Entry(istat_w, text= TCO2_istat_txt, font= txt).grid(row= 4, column= 2)
                    Label(istat_w, text= "HCO3: ", font= txt).grid(row= 5, column= 1)
                    HCO3_e = Entry(istat_w, text= HCO3_txt, font= txt).grid(row= 5, column= 2)
                    Label(istat_w, text= "BE: ", font= txt).grid(row= 6, column= 1)
                    BE_e = Entry(istat_w, text= BE_txt, font= txt).grid(row= 6, column= 2)
                    Label(istat_w, text= "sO2: ", font= txt).grid(row= 7, column= 1)
                    sO2_e = Entry(istat_w, text= sO2_txt, font= txt).grid(row= 7, column= 2)
                    Label(istat_w, text= "Hb: ", font= txt).grid(row= 8, column= 1)
                    Hb_e = Entry(istat_w, text= Hb_txt, font= txt).grid(row= 8, column= 2)

                    #Piccolo
                    Na_txt, K_txt, TCO2_pic_txt, Cl_txt = StringVar(), StringVar(), StringVar(), StringVar()
                    Glu_txt, Ca_txt, BUN_txt, Cre_txt = StringVar(), StringVar(), StringVar(), StringVar()
                    eGFR_txt, ALP_txt, AST_txt, TBIL_txt = StringVar(), StringVar(), StringVar(), StringVar()
                    ALB_txt, TP_txt = StringVar(), StringVar()

                    Label(pic_w, text= "Piccolo Measurements:", font= header).grid(row= 0, column= 4)
                    Label(pic_w, text= "Na: ", font= txt).grid(row= 1, column= 3)
                    Na_e = Entry(pic_w, text= Na_txt, font= txt).grid(row= 1, column= 4)
                    Label(pic_w, text= "K: ", font= txt).grid(row= 2, column= 3)
                    K_e = Entry(pic_w, text= K_txt, font= txt).grid(row= 2, column= 4)
                    Label(pic_w, text= "TCO2: ", font= txt).grid(row= 3, column= 3)
                    TCO2_pic_e = Entry(pic_w, text= TCO2_pic_txt, font= txt).grid(row= 3, column= 4)
                    Label(pic_w, text= "Cl: ", font= txt).grid(row= 4, column= 3)
                    Cl_e = Entry(pic_w, text= Cl_txt, font= txt).grid(row= 4, column= 4)
                    Label(pic_w, text= "Glu: ", font= txt).grid(row= 5, column= 3)
                    Glu_e = Entry(pic_w, text= Glu_txt, font= txt).grid(row= 5, column= 4)
                    Label(pic_w, text= "Ca: ", font= txt).grid(row= 6, column= 3)
                    Ca_e = Entry(pic_w, text= Ca_txt, font= txt).grid(row= 6, column= 4)
                    Label(pic_w, text= "BUN: ", font= txt).grid(row= 7, column= 3)
                    BUN_e = Entry(pic_w, text= BUN_txt, font= txt).grid(row= 7, column= 4)
                    Label(pic_w, text= "Cre: ", font= txt).grid(row= 8, column= 3)
                    Cre_e = Entry(pic_w, text= Cre_txt, font= txt).grid(row= 8, column= 4)
                    Label(pic_w, text= "eGFR: ", font= txt).grid(row= 9, column= 3)
                    eGFR_e = Entry(pic_w, text= eGFR_txt, font= txt).grid(row= 9, column= 4)
                    Label(pic_w, text= "ALP: ", font= txt).grid(row= 10, column= 3)
                    ALP_e = Entry(pic_w, text= ALP_txt, font= txt).grid(row= 10, column= 4)
                    Label(pic_w, text= "AST: ", font= txt).grid(row= 11, column= 3)
                    AST_e = Entry(pic_w, text= AST_txt, font= txt).grid(row= 11, column= 4)
                    Label(pic_w, text= "TBIL: ", font= txt).grid(row= 12, column= 3)
                    TBIL_e = Entry(pic_w, text= TBIL_txt, font= txt).grid(row= 12, column= 4)
                    Label(pic_w, text= "ALB: ", font= txt).grid(row= 13, column= 3)
                    ALB_e = Entry(pic_w, text= ALB_txt, font= txt).grid(row= 13, column= 4)
                    Label(pic_w, text= "TP: ", font= txt).grid(row= 14, column= 3)
                    TP_e = Entry(pic_w, text= TP_txt, font= txt).grid(row= 14, column= 4)

                    submit_istat = Button(istat_w, text= "Submit", command= lambda: upload("istat"), font= txt).grid(row= 9, column= 2, pady= chemsub_pady)
                    submit_pic = Button(pic_w, text= "Submit", command= lambda: upload("pic"), font= txt).grid(row= 15, column= 4, pady= chemsub_pady)

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
 
                    Label(ch_w, text= "Sensor data collection chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.7, anchor= CENTER)
                    user_guide_1 = "Plug in the devices in the following order:\n- Medtronic Bioconsole\n- Medtronic Biotrend\n- Force transducers (kidney scale, then urine scale)"
                    Label(port_w, text= user_guide_1, font= txt).place(relx= 0.5, rely= 0.3, anchor= CENTER)
                    port_check = Button(port_w, text= "Click to check port status", command= port_detect, font= txt).place(relx= 0.5, rely= 0.65, anchor= CENTER)
    else:
        Label(ch_w, text= "Selection already made.\nRestart to choose a new option.", font= txt, padx= allset_pad).place(relx= 0.5, rely= 0.7, anchor= CENTER)
        Label(unos_w, text= "UNOS ID already set.", font= txt, padx= 60, pady= u_pady).place(relx= 0.5, rely= 0.6, anchor= CENTER)
 
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
R2 = Radiobutton(ch_w, text= "Blood gas data upload", font= txt, variable= var, value= "2")
R2.place(relx= radx, rely= 0.4, anchor= W)
R3 = Radiobutton(ch_w, text= "Sensor data collection", font= txt, variable= var, value= "3")
R3.place(relx= radx, rely= 0.5, anchor= W)

Label(unos_w, text= "Enter UNOS ID (case sensitive):", font= txt).place(relx= 0.5, rely= 0.15, anchor= CENTER)
unos = Entry(unos_w, text= unos_txt, font= txt)
unos.place(relx= 0.5, rely= 0.35, anchor= CENTER)
submit = Button(opts_w, text= "Submit", font= txt, command= choice).grid(row= 2, column= 0, pady= 5, ipadx= sub_pad)
restart = Button (opts_w, text= "Restart", font= txt, command= anew).grid(row= 2,column= 1, pady= 5, ipadx= rest_pad)
exit = Button(opts_w, text= "Exit", font= txt, command= lambda: q("set")).grid(row= 2, column= 2, pady= 5, ipadx= ex_pad)

root.mainloop()
