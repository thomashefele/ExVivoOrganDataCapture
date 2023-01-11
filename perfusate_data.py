from tkinter import *
from tkinter import ttk
import pyodbc, os, platform, sys

if platform.system() == "Linux":
    if os.environ.get('DISPLAY','') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')

#Establish database connection
dsn = 'DTKserverdatasource'
user = 'dtk_lab@dtk-server'
password = 'data-collection1'
database = 'perf-data'
connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)

#This block of code retrieves the UNOS ID from the organ donor database so that it may be associated to all other data collected.
with pyodbc.connect(connString) as cnxn_unos:
    with cnxn_unos.cursor() as cursor:
        cursor.execute("SELECT TOP 1 UNOS_ID FROM dbo.organ_t ORDER BY time_stamp DESC;") 
        row = cursor.fetchone()

#This function generates an error window if anything besides a numeric value is entered into the app.
def error():
    err_win = Tk()
    err_win.title("Error!")
    err_win.geometry("500x50")
    error = Label(err_win, text= "Invalid data type entered. Please re-enter data again in float format.")
    error.place(relx= 0.5, rely= 0.5, anchor= CENTER)
    
#The upload functions below retreive the numeric strings from the input of the app, converts the strings to float values, and then upload the values to
#to the DTK database
def upload_istat():
    try:
        with pyodbc.connect(connString) as cnxn_istat:
            with cnxn_istat.cursor() as cursor:    
                pH, PCO2, PO2 = float(pH_txt.get()), float(PCO2_txt.get()), float(PO2_txt.get())
                TCO2_istat, HCO3, BE = float(TCO2_istat_txt.get()), float(HCO3_txt.get()), float(BE_txt.get())
                sO2, Hb = float(sO2_txt.get()), float(Hb_txt.get())
                execstr = "INSERT INTO dbo.istat_t([UNOS_ID], [time_stamp], [ph], [pco2], [po2], [tco2], [hco3], [be], [so2], [hb]) VALUES('{}', GETDATE(), {}, {}, {}, {}, {}, {}, {}, {});".format(row[0], pH, PCO2, PO2, TCO2_istat, HCO3, BE, sO2, Hb)
                cursor.execute(execstr)
                cnxn_istat.commit()    
                Label(istat_tab, text= "Data successfully uploaded!").grid(row= 11, column= 2)
    except ValueError:
        error()
    
def upload_pic():
    try:
        with pyodbc.connect(connString) as cnxn_pic:
            with cnxn_pic.cursor() as cursor: 
                Na, K, TCO2_pic = float(Na_txt.get()), float(K_txt.get()), float(TCO2_pic_txt.get())
                Cl, Glu, Ca = float(Cl_txt.get()), float(Glu_txt.get()), float(Ca_txt.get())
                BUN, Cre, eGFR = float(BUN_txt.get()), float(Cre_txt.get()), float(eGFR_txt.get())
                ALP, AST, TBIL = float(ALP_txt.get()), float(AST_txt.get()), float(TBIL_txt.get())
                ALB, TP = float(ALB_txt.get()), float(TP_txt.get())
                execstr = "INSERT INTO dbo.pic_t([UNOS_ID], [time_stamp], [Na], [K], [tco2], [Cl], [glu], [Ca], [BUN], [cre], [egfr], [alp], [ast], [tbil], [alb], [tp]) VALUES('{}', GETDATE(), {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {});".format(row[0], Na, K, TCO2_pic, Cl, Glu, Ca, BUN, Cre, eGFR, ALP, AST, TBIL, ALB, TP) 
                cursor.execute(execstr)
                cnxn_pic.commit()   
                Label(pic_tab, text= "Data successfully uploaded!").grid(row= 17, column= 2)       
    except ValueError:
        error()

#The code below initializes the windows and tabs for the app. 
app = Tk()
app.title("Kidney Perfusate Data")
app.geometry("350x525")
tabs = ttk.Notebook(app)
istat_tab = ttk.Frame(tabs)
tabs.add(istat_tab, text= "iStat Measurements")
pic_tab = ttk.Frame(tabs)
tabs.add(pic_tab, text= "Piccolo Measurements")
tabs.pack(expand= 1, fill="both")

pH_txt, PCO2_txt, PO2_txt, TCO2_istat_txt = StringVar(), StringVar(), StringVar(), StringVar()
HCO3_txt, BE_txt, sO2_txt, Hb_txt = StringVar(), StringVar(), StringVar(), StringVar()

#iStat tab
Label(istat_tab, text= "iStat").grid(row= 1, column= 2)

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

Na_txt, K_txt, TCO2_pic_txt, Cl_txt = StringVar(), StringVar(), StringVar(), StringVar()
Glu_txt, Ca_txt, BUN_txt, Cre_txt = StringVar(), StringVar(), StringVar(), StringVar()
eGFR_txt, ALP_txt, AST_txt, TBIL_txt = StringVar(), StringVar(), StringVar(), StringVar()
ALB_txt, TP_txt = StringVar(), StringVar()

#Piccolo tab
Label(pic_tab, text= "Piccolo").grid(row= 1, column= 2)

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

app.mainloop()
