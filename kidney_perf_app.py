import serial as ser, numpy as np, simpleaudio as sa
import pyodbc, serial.tools.list_ports, os, sys, platform
from time import monotonic, sleep
from datetime import datetime, timedelta
from tkinter import *
from threading import Thread

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
sub_pad,rest_pad,ex_pad = 1, 1, 5
file = os.path.abspath(__file__)
OS = platform.system()

if w >= 1440 and h >= 900:
    head_sz, txt_sz = 25, 20
    of_x,of_y = 0.36, 0.95
    df_x,df_y = 0.61, 0.95
    cf_x,cf_y = 0.34, 0.42
    radx = 0.25
    uf_x,uf_y = 0.34, 0.38
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
    sub_pad,rest_pad,ex_pad = 5, 5, 15

var,unos_txt = StringVar(), StringVar()
lap, perf_time, name, baud_rate, t_o = 5, 29000, [], [9600,2400], [5.1, 5.2, 0.2]
CHOOSE_AGN, CHECK_AGAIN, STOP = False, False, False
null_input, nan, connString = "b\'\'", float("nan"), None

#The code below establishes the necessary information to interact with the given OS. Note: although the GUI was designed on a Mac, 
#the full software does not function on Mac.
if OS == "Linux":
    rest_comm = "python3 kidney_perf_app.py"
    
    dsn = "DTKserverdatasource"
    user = "dtk_lab@dtk-server"
    password = "data-collection1"
    database = "perf-data"
    connString = "DSN={0};UID={1};PWD={2};DATABASE={3};".format(dsn,user,password,database)
    
elif OS == "Windows":
    rest_comm = "start {0}".format(file)
    
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
            alert = sa.play_buffer(aud, 1, 2, N)
        return data

    if data_str == null_input:
        alert = sa.play_buffer(aud, 1, 2, N)
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
                            alert = sa.play_buffer(aud, 1, 2, N)
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
                                alert = sa.play_buffer(aud, 1, 2, N)
                                execstr = "INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                                cursor.execute(execstr)
                    except (OSError, FileNotFoundError):
                        MT_port.close()
                        alert = sa.play_buffer(aud, 1, 2, N)
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
                        alert = sa.play_buffer(aud, 1, 2, N)
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
                                            alert = sa.play_buffer(aud, 1, 2, N)
                                            execstr = "INSERT INTO dbo.km_t([UNOS_ID], [time_stamp]) VALUES('{}', GETDATE());".format(unos_ID)
                                            cursor.execute(execstr)
                                        else:
                                            execstr = "INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{}', GETDATE(), {});".format(unos_ID, mass)
                                            cursor.execute(execstr)
                                        ts_km = Label(vals, text= "{}".format(datetime.now().strftime("%H:%M:%S")), font= txt, bg= "white", padx= 5)
                                        ts_km.place(relx= tsx, rely= 0.6, anchor= CENTER) 
                                    elif measure == "uo":
                                        if sleepy:
                                            alert = sa.play_buffer(aud, 1, 2, N)
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
    t_init = datetime.now()
    t_end = t_init + timedelta(hours= 8)
    Label(disp_w, text= "Data collection started at: {0}; stop at: {1}.".format(t_init.strftime("%H:%M:%S"),t_end.strftime("%H:%M:%S")), font= txt).place(relx= 0.5, rely= 0.2, anchor= CENTER)
    
    MT_thread = Thread(target= MT, args= (name[0], baud_rate[0], t_o[0]),)
    BT_thread = Thread(target= BT, args= (name[1], baud_rate[0], t_o[1]),)
    FT_1_thread = Thread(target= FT, args= (name[2], baud_rate[1], t_o[2], lap, "km"),)
    FT_2_thread = Thread(target= FT, args= (name[3], baud_rate[1], t_o[2], lap, "uo"),)

    MT_thread.start()
    BT_thread.start()
    FT_1_thread.start()
    FT_2_thread.start()
    
    halt = Button(disp_w, text= "Stop Data Collection", font= txt, padx= 30, command= lambda: q("data"))
    halt.place(relx= 0.5, rely= 0.1, anchor= CENTER)

    after(1000*perf_time, lambda: q("data"))
    
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
            Label(port_w, text= "No sensors connected", font= txt, padx= prt_padx).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 1:
            Label(port_w, text= "Only 1 sensor is connected. Plug all in the correct order", font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 2 or Nusb == 3:
            Label(port_w, text= "Only {} sensors are connected. Plug all in the correct order".format(Nusb), font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
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

                if sel == "1":
                    Label(ch_w, text= "Donor information upload chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.7, anchor= CENTER)
                elif sel == "2":
                    Label(ch_w, text= "Blood gas data upload chosen.", font= txt, padx= 15).place(relx= 0.5, rely= 0.7, anchor= CENTER)

                    istat_w = Frame(data_w, width= chemf_x*w, height= chemf_y*h, bd= 2, relief= "sunken")
                    istat_w.grid(row= 0,  column= 0, padx= 10, pady= 10)
                    istat_w.grid_propagate(False)
                    pic_w = Frame(data_w, width= chemf_x*w, height= chemf_y*h, bd= 2, relief= "sunken")
                    pic_w.grid(row= 0,  column= 1, padx= 10, pady= 10)
                    pic_w.grid_propagate(False)

                    #The functions below are necessary for the chem gas app to work. 
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

                    #Piccolo tab
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
                    user_guide_1 = "Plug in the devices in the following order:\n- Medtronic Bioconsole\n- Medtronic Biotrend\n- Force transducers (any order)"
                    Label(port_w, text= user_guide_1, font= txt).place(relx= 0.5, rely= 0.3, anchor= CENTER)
                    port_check = Button(port_w, text= "Click to check port status", command= port_detect, font= txt).place(relx= 0.5, rely= 0.65, anchor= CENTER)
    else:
        Label(ch_w, text= "Selection already made.\nRestart to choose a new option.", font= txt, padx= allset_pad).place(relx= 0.5, rely= 0.7, anchor= CENTER)
        Label(unos_w, text= "UNOS ID already set.", font= txt, padx= 40).place(relx= 0.5, rely= 0.6, anchor= CENTER)
 
#Now that the GUI has been initialized and all the functions ready for execution, the block of code below establishes the widgets necessary
#for the user to interact with the program.
opts_w = LabelFrame(root, text= "Settings:", width= of_x*w, height= of_y*h, bd= 2, relief= "raised", font= header)
opts_w.grid(row= 0, column= 0, padx= 10, pady= 10)
opts_w.grid_propagate(False)
data_w = LabelFrame(root, text= "Data Input:", width= df_x*w, height= df_y*h, bd= 2, relief= "raised", font= header)
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

Label(unos_w, text= "Enter UNOS ID:", font= txt).place(relx= 0.5, rely= 0.15, anchor= CENTER)
unos = Entry(unos_w, text= unos_txt, font= txt)
unos.place(relx= 0.5, rely= 0.35, anchor= CENTER)
submit = Button(opts_w, text= "Submit", font= txt, command= choice).grid(row= 2, column= 0, pady= 5, ipadx= sub_pad)
restart = Button (opts_w, text= "Restart", font= txt, command= anew).grid(row= 2,column= 1, pady= 5, ipadx= rest_pad)
exit = Button(opts_w, text= "Exit", font= txt, command= lambda: q("set")).grid(row= 2, column= 2, pady= 5, ipadx= ex_pad)

root.mainloop()
