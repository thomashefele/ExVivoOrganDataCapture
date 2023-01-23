from tkinter import *
from tkinter import ttk
from time import sleep
import serial as ser
import serial.tools.list_ports
from threading import Thread
from random import randint

root = Tk()
root.title("Kidney Perfusion App") 
root.attributes("-fullscreen", True)
w,h = root.winfo_screenwidth(), root.winfo_screenheight()
root.config(bg= "RoyalBlue1")
header,txt = ("Helvetica", 30, "bold"), ("Helvetica", 20)
var,unos_txt = StringVar(), StringVar()
unos_ID, Nusb, lap, name = None, None, 5, []
CHOOSE_AGN, CHECK_AGAIN, STOP = False, False, False
perf_time = 30

def anew():
    os.system("command tbd")
    root.destroy()

def clear(win):
    if win == "data_w":
        for widgets in data_w.winfo_children():
            widgets.destroy()
    elif win == "port_w":
        for widgets in port_w.winfo_children():
            widgets.destroy()
    elif win == "disp_w":
        for widgets in port_w.winfo_children():
            widgets.destroy()

def unos_save():
    global unos_ID
    unos_ID = unos_txt.get()
        
    if unos_ID == "":
        Label(unos_w, text= "Blank UNOS ID entered.", font= txt).grid(row= 2, column= 0, columnspan= 2, padx= 5, pady= 40, ipadx= 10)
    else:
        Label(unos_w, text= "UNOS ID successfully set.", font= txt).grid(row= 2, column= 0, columnspan= 2, padx= 5, pady= 40, ipadx= 10)

def start_coll():
    Label(disp_w, text= "Data collection in progress.", font= txt, padx= 30).place(relx= 0.5, rely= 0.2, anchor= CENTER)
    
    def MT():
        global N
        while STOP == False:
            N = randint(0,100)
            print(N)
            Label(disp_w, text= "{}".format(N), font= txt).place(relx= 0.1, rely= 0.4)
            sleep(1)
    
    MT_thread = Thread(target= MT)
    MT_thread.start()
    exit = Button(disp_w, text= "Exit Data Collection", font= txt, padx= 30, command= q)
    exit.place(relx= 0.5, rely= 0.1, anchor= CENTER)
    root.after(1000*perf_time, q)
    
def q():
    global STOP
    STOP = True
    Label(disp_w, text= "Data collection complete. Goodbye!", font= txt).place(relx= 0.5, rely= 0.2, anchor= CENTER)
        
def port_detect():
    global Nusb
    global name
    global CHECK_AGAIN
    ports = serial.tools.list_ports.comports()
    for dev,descr,hwid in sorted(ports):
            if dev.find("COM") != -1 or dev.find("USB") != -1 or dev.find("usbserial") != -1:
                name.append(dev)
            else:
                pass
    Nusb = len(name)

    if Nusb != 0:
        if Nusb == 6:
            Label(port_w, text= "No sensors connected", font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 1:
            Label(port_w, text= "Only 1 sensor is connected.\nPlug all in the correct order".format(Nusb), font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 2:
            Label(port_w, text= "Only {} sensors are connected:\nPlug all in the correct order".format(Nusb), font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        elif Nusb == 3:
            Label(port_w, text= "Only {} sensors are connected:\nPlug all in the correct order".format(Nusb), font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
        else:
            pass
        name = []

    elif Nusb == 0 and CHECK_AGAIN == False:
        Label(port_w, text= "Data collection ready to commence!", font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)     
        CHECK_AGAIN = True
        collecting = Button(disp_w, text= "Start Data Collection", font= txt, command= start_coll).place(relx= 0.5, rely= 0.1, anchor= CENTER)
    elif Nusb == 0 and CHECK_AGAIN == True:
        Label(port_w, text= "Data collection ready to commence!", font= txt).place(relx= 0.5, rely= 0.85, anchor= CENTER)
                
def choice():
    global CHOOSE_AGN
    
    if CHOOSE_AGN == False:
        unos_save()
        sel = var.get()

        if unos_ID == "" or unos_ID ==  None:
            if sel == "1" or sel == "2" or sel == "3":
                Label(data_w, text= "Enter a UNOS ID to proceed.", font= txt, padx= 200).place(relx= 0.5, rely= 0.5, anchor= CENTER)
            else:
                Label(data_w, text= "Select an option and enter a UNOS ID to proceed.", font= txt).place(relx= 0.5, rely= 0.5, anchor= CENTER)
                Label(ch_w, text= "No selection made.", font= txt).grid(row= 5, column= 0, columnspan= 2, padx= 5, pady= 30, ipadx= 40)
        else:
            if sel == "1":
                CHOOSE_AGN = True
                clear("data_w")
                Label(ch_w, text= "Donor information upload chosen.", font= txt).grid(row= 5, column= 0, columnspan= 2, padx= 5, pady= 30, ipadx= 10)
            elif sel == "2":
                CHOOSE_AGN = True
                clear("data_w")
                Label(ch_w, text= "Blood gas data upload chosen.", font= txt).grid(row= 5, column= 0, columnspan= 2, padx= 5, pady= 30, ipadx= 10)

                istat_w = Frame(data_w, width= 0.29*w, height= 0.8*h, bd= 2, relief= "sunken")
                istat_w.grid(row= 0,  column= 0, padx= 10, pady= 10)
                istat_w.grid_propagate(False)
                pic_w = Frame(data_w, width= 0.29*w, height= 0.8*h, bd= 2, relief= "sunken")
                pic_w.grid(row= 0,  column= 1, padx= 10, pady= 10)
                pic_w.grid_propagate(False)

                #The functions below are necessary for the chem gas app to work. 
                def upload_istat():
                    try:  
                        pH, PCO2, PO2 = float(pH_txt.get()), float(PCO2_txt.get()), float(PO2_txt.get())
                        TCO2_istat, HCO3, BE = float(TCO2_istat_txt.get()), float(HCO3_txt.get()), float(BE_txt.get())
                        sO2, Hb = float(sO2_txt.get()), float(Hb_txt.get())
                        Label(istat_w, text= "Data successfully uploaded!", font= txt, padx= 20).grid(row= 10, column= 2)
                    except ValueError:
                        Label(istat_w, text= "Invalid data type or blank entry", font= txt).grid(row= 10, column= 2) 

                def upload_pic():
                    try:
                        Na, K, TCO2_pic = float(Na_txt.get()), float(K_txt.get()), float(TCO2_pic_txt.get())
                        Cl, Glu, Ca = float(Cl_txt.get()), float(Glu_txt.get()), float(Ca_txt.get())
                        BUN, Cre, eGFR = float(BUN_txt.get()), float(Cre_txt.get()), float(eGFR_txt.get())
                        ALP, AST, TBIL = float(ALP_txt.get()), float(AST_txt.get()), float(TBIL_txt.get())
                        ALB, TP = float(ALB_txt.get()), float(TP_txt.get())
                        Label(pic_w, text= "Data successfully uploaded!", font= txt, padx= 20).grid(row= 16, column= 4)       
                    except ValueError:
                        Label(pic_w, text= "Invalid data type or blank entry.", font= txt).grid(row= 16, column= 4) 

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

                submit_istat = Button(istat_w, text= "Submit", command= upload_istat, font= txt).grid(row= 9, column= 2, pady= 30)
                submit_pic = Button(pic_w, text= "Submit", command= upload_pic, font= txt).grid(row= 15, column= 4, pady= 30)

            elif sel == "3":
                CHOOSE_AGN = True
                clear("data_w")
                global port_w
                global disp_w
                port_w = Frame(data_w, width= 0.59*w, height= 0.25*h, bd = 2, relief= "sunken")
                port_w.grid(row= 0, column= 0, padx= 10, pady= 10)
                port_w.grid_propagate(False)
                disp_w = Frame(data_w, width= 0.59*w, height= 0.6*h, bd = 2, relief= "sunken")
                disp_w.grid(row= 1, column= 0, padx= 10, pady= 10)
                disp_w.grid_propagate(False)

                Label(ch_w, text= "Sensor data collection chosen.", font= txt).grid(row= 5, column= 0, columnspan= 2, padx= 5, pady= 30, ipadx= 10)
                user_guide_1 = "Plug in the devices in the following order:\n- Medtronic Bioconsole\n- Medtronic Biotrend\n- Force transducers (any order)"
                Label(port_w, text= user_guide_1, font= txt).place(relx= 0.5, rely= 0.3, anchor= CENTER)
                port_check = Button(port_w, text= "Click to check port status", command= port_detect, font= txt).place(relx= 0.5, rely= 0.65, anchor= CENTER)

            else:
                Label(data_w, text= "Select an option.", font= txt, padx= 200).place(relx= 0.5, rely= 0.5, anchor= CENTER)
                Label(ch_w, text= "No selection made.", font= txt).grid(row= 5, column= 0, columnspan= 2, padx= 5, pady= 30, ipadx= 40)
    else:
        CHOOSE_AGN = True
        Label(ch_w, text= "Selection already made.\nExit and restart to choose\na new option.", font= txt).grid(row= 5, column= 0, columnspan= 2, padx= 5, pady= 30, ipadx= 40)
        Label(unos_w, text= "UNOS ID already set.", font= txt, padx= 120).grid(row= 2, column= 0, columnspan= 2, pady= 40, ipadx= 10)
    
opts_w = LabelFrame(root, text= "Settings:", width= 0.36*w, height= 0.95*h, bd= 2, relief= "raised", font= header)
opts_w.grid(row= 0, column= 0, padx= 10, pady= 10)
opts_w.grid_propagate(False)
data_w = LabelFrame(root, text= "Data Input:", width= 0.61*w, height= 0.95*h, bd= 2, relief= "raised", font= header)
data_w.grid(row= 0, column= 1, padx= 10, pady= 10)
data_w.grid_propagate(False)

ch_w = Frame(opts_w, bd = 2, width= 0.34*w, height= 0.42*h, relief= "sunken")
ch_w.grid(row= 0, column= 0, columnspan= 2, padx= 10, pady= 10)
ch_w.grid_propagate(False)
unos_w = Frame(opts_w, bd = 2, width= 0.34*w, height= 0.38*h, relief= "sunken")
unos_w.grid(row= 1, column= 0, columnspan= 2, padx= 10, pady= 10)
unos_w.grid_propagate(False)

Label(ch_w, text= "Select which of the below that you would like to do:", font= txt).grid(row= 0, column= 0, columnspan= 2, padx= 10, pady= 30)
R1 = Radiobutton(ch_w, text= "Donor information upload", font= txt, variable= var, value= "1")
R1.grid(row= 1, column= 0, columnspan= 2, padx= 5, pady= 5)
R2 = Radiobutton(ch_w, text= "Blood gas data upload", font= txt, variable= var, value= "2")
R2.grid(row= 2, column= 0, columnspan= 2, padx= 5, pady= 5)
R3 = Radiobutton(ch_w, text= "Sensor data collection", font= txt, variable= var, value= "3")
R3.grid(row= 3, column= 0, columnspan= 2, padx= 5, pady= 5)
Label(ch_w, text= "", font= txt).grid(row= 5, column= 0, padx= 5, pady= 5)

Label(unos_w, text= "Enter UNOS ID:", font= txt).grid(row= 0, column= 0, padx= 30, pady= 30) 
unos = Entry(unos_w, text= unos_txt, font= txt)
unos.grid(row= 0, column= 1, pady= 20)
Label(unos_w, text= "", font= txt).grid(row= 2, column= 0, padx= 5, pady= 10)
submit = Button(opts_w, text= "Submit", font= txt, command= choice).grid(row= 2, column= 0, pady= 5, ipadx= 60)
exit = Button(opts_w, text= "Exit", font= txt, command= root.destroy).grid(row= 2, column= 1, pady= 5, ipadx= 80)
restart = Button (opts_w, text= "Restart", font= txt, command= anew).grid(row= 2,column= 1, pady= 5, ipadx= 5)

root.mainloop()
