from tkinter import * 
from tkinter import ttk
import pyodbc, serial.tools.list_ports, os, sys, platform
from time import sleep, time
from datetime import timedelta
from random import random

def port_detect():
    name = []
    ports = serial.tools.list_ports.comports()
    for dev,descr,hwid in sorted(ports):
            if dev.find("COM") != -1 or dev.find("USB") != -1 or dev.find("cu") != -1:
                    name.append(dev)
            else:
                    pass
    Nusb = len(name)
    
    if Nusb != 2:
        if Nusb == 0:
            Label(port_win, text= "No sensors connected".format(Nusb)).place(relx= 0.5, rely= 0.6, anchor= CENTER)
        elif Nusb == 1:
            Label(port_win, text= "Only 1 sensor is connected:\n- Medtronic Bioconsole".format(Nusb)).place(relx= 0.5, rely= 0.6, anchor= CENTER)
        elif Nusb == 26:
            Label(port_win, text= "Only {} sensors are connected:\n- Medtronic Bioconsole\n- Medtronic Biotrend".format(Nusb)).place(relx= 0.5, rely= 0.6, anchor= CENTER)
        elif Nusb == 3:
            Label(port_win, text= "Only {} sensors are connected:\n- Medtronic Bioconsole\n- Medtronic Biotrend\n- 1 Force transducer".format(Nusb)).place(relx= 0.5, rely= 0.6, anchor= CENTER)
        else:
            pass
    elif Nusb == 2:
        Label(port_win, text= "Data collection ready to commence!").place(relx= 0.5, rely= 0.5, anchor= CENTER)
        port_win.after(2000, port_win.destroy)
    
port_win = Tk()
port_win.title("Start Up")
port_win.geometry("300x250")
user_guide = "Plug in the devices in the following order:\n- Medtronic Bioconsole\n- Medtronic Biotrend\n- Force transducers (any order)"
Label(port_win, text= user_guide).place(relx= 0.5, rely= 0.2, anchor= CENTER)
port_check = Button(port_win, text= "Click to check port status", command= port_detect).place(relx= 0.5, rely= 0.4, anchor= CENTER)
port_win.mainloop()

def unos_save():
    global unos_ID
    unos_ID = unos_txt.get()
    if unos_ID == "":
        unos_error()
    else:
        unos_win.destroy()

def realtime():
    Label(data_tab, text= "Perfusion time: {}".format(timedelta(seconds= round(time()-start)))).grid(row= 1, column= 1)
    P, Q = float("nan"),round(random(),3)
    Label(data_tab, text= "Pa (mmHg): {} Qa (L/min): {}".format(P, Q), padx= 20).grid(row= 2, column= 1)
    Vs, hct = round(random(),3),round(random(),3)
    Label(data_tab, text= "Ven sO2 (%): {} Hct (%): {}".format(Vs, hct), padx= 20).grid(row= 3, column= 1)
    km, uo = round(random(),3),round(random(),3)
    Label(data_tab, text= "Kidney Weight (kg): {}".format(km), padx= 20).grid(row= 4, column= 1)
    Label(data_tab, text= "Urine Output (kg): {}".format(uo), padx= 20).grid(row= 5, column= 1)
    if STOP == False:
        data_tab.after(1000, realtime)
    elif STOP == True:
        Label(data_tab, text= "Data collection complete!").grid(row= 7, column= 1)

def unos_error():
    err_win = Tk()
    err_win.title("Error!")
    err_win.geometry("250x50")
    error = Label(err_win, text= "Blank UNOS ID entered.")
    error.place(relx= 0.5, rely= 0.3, anchor= CENTER)

def dt_error():
    err_win = Tk()
    err_win.title("Error!")
    err_win.geometry("500x50")
    error = Label(err_win, text= "Invalid data type entered. Please re-enter data again in float format.")
    error.place(relx= 0.5, rely= 0.3, anchor= CENTER)
    
def sens_asleep():
    err_win = Tk()
    err_win.title("Warning!")
    err_win.geometry("250x50")
    error = Label(err_win, text= "A sensor has fallen asleep.")
    error.place(relx= 0.5, rely= 0.3, anchor= CENTER)

def upload_istat():
    try:  
        pH, PCO2, PO2 = float(pH_txt.get()), float(PCO2_txt.get()), float(PO2_txt.get())
        TCO2_istat, HCO3, BE = float(TCO2_istat_txt.get()), float(HCO3_txt.get()), float(BE_txt.get())
        sO2, Hb = float(sO2_txt.get()), float(Hb_txt.get()) 
        Label(istat_tab, text= "Data successfully uploaded!").grid(row= 11, column= 2)
    except ValueError:
        dt_error()
    
def upload_pic():
    try:
        Na, K, TCO2_pic = float(Na_txt.get()), float(K_txt.get()), float(TCO2_pic_txt.get())
        Cl, Glu, Ca = float(Cl_txt.get()), float(Glu_txt.get()), float(Ca_txt.get())
        BUN, Cre, eGFR = float(BUN_txt.get()), float(Cre_txt.get()), float(eGFR_txt.get())
        ALP, AST, TBIL = float(ALP_txt.get()), float(AST_txt.get()), float(TBIL_txt.get())
        ALB, TP = float(ALB_txt.get()), float(TP_txt.get())  
        Label(pic_tab, text= "Data successfully uploaded!").grid(row= 17, column= 2)       
    except ValueError:
        dt_error()

#UNOS ID setup
unos_win = Tk()
unos_win.title("UNOS ID")
unos_win.geometry("300x100")
Label(unos_win, text= "Enter UNOS ID for this case: ").place(relx= 0.5, rely= 0.2, anchor= CENTER)
unos_txt = StringVar()
unos = Entry(unos_win, text= unos_txt).place(relx= 0.5, rely= 0.5, anchor= CENTER)
submit_unos = Button(unos_win, text= "Submit", command= unos_save).place(relx= 0.5, rely= 0.8, anchor= CENTER)
unos_win.mainloop()

#The code below initializes the windows and tabs for the app. 
app = Tk()
app.title("Kidney Perfusion Data")
app.geometry("300x500")
tabs = ttk.Notebook(app)
istat_tab = ttk.Frame(tabs)
tabs.add(istat_tab, text= "iStat")
pic_tab = ttk.Frame(tabs)
tabs.add(pic_tab, text= "Piccolo")
data_tab = ttk.Frame(tabs)
tabs.add(data_tab, text= "Sensors")
tabs.pack(expand= 1, fill="both")

start = time()
data_tab.after(1000, realtime)

#iStat tab
pH_txt, PCO2_txt, PO2_txt, TCO2_istat_txt = StringVar(), StringVar(), StringVar(), StringVar()
HCO3_txt, BE_txt, sO2_txt, Hb_txt = StringVar(), StringVar(), StringVar(), StringVar()

Label(istat_tab, text= "pH: ").grid(row= 2, column= 1)
pH_e = Entry(istat_tab, text= pH_txt).grid(row= 2, column= 2)
Label(istat_tab, text= "PCO2: ").grid(row= 3, column= 1)
PCO2_e = Entry(istat_tab, text= PCO2_txt).grid(row= 3, column= 2)
Label(istat_tab, text= "PO2: ").grid(row= 4, column= 1)
PO2_e = Entry(istat_tab, text= PO2_txt).grid(row= 4, column= 2)
Label(istat_tab, text= "TCO2: ").grid(row= 5, column= 1)
TCO2_istat_e = Entry(istat_tab, text= TCO2_istat_txt).grid(row= 5, column= 2)
Label(istat_tab, text= "HCO3: ").grid(row= 6, column= 1)
HCO3_e = Entry(istat_tab, text= HCO3_txt).grid(row= 6, column= 2)
Label(istat_tab, text= "BE: ").grid(row= 7, column= 1)
BE_e = Entry(istat_tab, text= BE_txt).grid(row= 7, column= 2)
Label(istat_tab, text= "sO2: ").grid(row= 8, column= 1)
sO2_e = Entry(istat_tab, text= sO2_txt).grid(row= 8, column= 2)
Label(istat_tab, text= "Hb: ").grid(row= 9, column= 1)
Hb_e = Entry(istat_tab, text= Hb_txt).grid(row= 9, column= 2)

submit_istat = Button(istat_tab, text= "Submit", command= upload_istat).grid(row= 10, column= 2)

STOP = False

def yes():
    global STOP
    STOP = True
    

#Piccolo tab
Na_txt, K_txt, TCO2_pic_txt, Cl_txt = StringVar(), StringVar(), StringVar(), StringVar()
Glu_txt, Ca_txt, BUN_txt, Cre_txt = StringVar(), StringVar(), StringVar(), StringVar()
eGFR_txt, ALP_txt, AST_txt, TBIL_txt = StringVar(), StringVar(), StringVar(), StringVar()
ALB_txt, TP_txt = StringVar(), StringVar()

Label(pic_tab, text= "Na: ").grid(row= 2, column= 1)
Na_e = Entry(pic_tab, text= Na_txt).grid(row= 2, column= 2)
Label(pic_tab, text= "K: ").grid(row= 3, column= 1)
K_e = Entry(pic_tab, text= K_txt).grid(row= 3, column= 2)
Label(pic_tab, text= "TCO2: ").grid(row= 4, column= 1)
TCO2_pic_e = Entry(pic_tab, text= TCO2_pic_txt).grid(row= 4, column= 2)
Label(pic_tab, text= "Cl: ").grid(row= 5, column= 1)
Cl_e = Entry(pic_tab, text= Cl_txt).grid(row= 5, column= 2)
Label(pic_tab, text= "Glu: ").grid(row= 6, column= 1)
Glu_e = Entry(pic_tab, text= Glu_txt).grid(row= 6, column= 2)
Label(pic_tab, text= "Ca: ").grid(row= 7, column= 1)
Ca_e = Entry(pic_tab, text= Ca_txt).grid(row= 7, column= 2)
Label(pic_tab, text= "BUN: ").grid(row= 8, column= 1)
BUN_e = Entry(pic_tab, text= BUN_txt).grid(row= 8, column= 2)
Label(pic_tab, text= "Cre: ").grid(row= 9, column= 1)
Cre_e = Entry(pic_tab, text= Cre_txt).grid(row= 9, column= 2)
Label(pic_tab, text= "eGFR: ").grid(row= 10, column= 1)
eGFR_e = Entry(pic_tab, text= eGFR_txt).grid(row= 10, column= 2)
Label(pic_tab, text= "ALP: ").grid(row= 11, column= 1)
ALP_e = Entry(pic_tab, text= ALP_txt).grid(row= 11, column= 2)
Label(pic_tab, text= "AST: ").grid(row= 12, column= 1)
AST_e = Entry(pic_tab, text= AST_txt).grid(row= 12, column= 2)
Label(pic_tab, text= "TBIL: ").grid(row= 13, column= 1)
TBIL_e = Entry(pic_tab, text= TBIL_txt).grid(row= 13, column= 2)
Label(pic_tab, text= "ALB: ").grid(row= 14, column= 1)
ALB_e = Entry(pic_tab, text= ALB_txt).grid(row= 14, column= 2)
Label(pic_tab, text= "TP: ").grid(row= 15, column= 1)
TP_e = Entry(pic_tab, text= TP_txt).grid(row= 15, column= 2)
submit_pic = Button(pic_tab, text= "Submit", command= upload_pic).grid(row= 16, column= 2)

exit = Button(data_tab, text= "Exit?", command= yes).grid(row= 6, column= 1)

app.mainloop()
