import pyodbc, platform
import random as rand
from time import time, sleep

#timer
start = time() 
lap = 0
interval = 3600

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


cnxn_don =  pyodbc.connect(connString)
cursor_don = cnxn_don.cursor()
cnxn_MT =  pyodbc.connect(connString)
cursor_MT = cnxn_MT.cursor()
cnxn_BT =  pyodbc.connect(connString)
cursor_BT = cnxn_BT.cursor()
cnxn_FT1 =  pyodbc.connect(connString)
cursor_FT1 = cnxn_FT1.cursor()
cnxn_FT2 =  pyodbc.connect(connString)
cursor_FT2 = cnxn_FT2.cursor()

i = 0

#data generator
while lap <= interval:
    
  if lap < (interval/2):
        unos_id = "TEST_ID_1"
        
        if i == 0:
            eth, gender, bt, age, bmi, weight = "Hispanic", "M", "O", "37", "23.4", "190"
            cursor_don.execute("INSERT INTO dbo.organ_t([UNOS_ID], [time_stamp], [blood_type], [weight], [age], [bmi], [gender], [eth_race]) VALUES('{}', GETDATE(), '{}', '{}', '{}', '{}', '{}', '{}');".format(unos_id, bt, weight, age, bmi, gender, eth))
            cnxn_don.commit()
            i = 1
    
  elif lap >= (interval/2):
        unos_id = "TEST_ID_2"
        
        if i == 1:
            eth, gender, bt, age, bmi, weight = "White", "F", "A", "24", "20.6", "155"
            cursor_don.execute("INSERT INTO dbo.organ_t([UNOS_ID], [time_stamp], [blood_type], [weight], [age], [bmi], [gender], [eth_race]) VALUES('{}', GETDATE(), '{}', '{}', '{}', '{}', '{}', '{}');".format(unos_id, bt, weight, age, bmi, gender, eth))
            cnxn_don.commit()
            i = 0
            
  #MedTronic data
  data_AF = round(rand.random(), 3)
  data_AP = round(5*rand.random(), 3)
  rpm = round(5000*rand.random())
  cursor_MT.execute("INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure], [rpm]) VALUES('{}', GETDATE(), {}, {}, {});".format(unos_id, data_AF, data_AP, rpm))
  cnxn_MT.commit()
  #Kidney mass data
  data_KM = round(5*rand.random(), 3)
  cursor_FT1.execute("INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{}', GETDATE(), {});".format(unos_id, data_KM))
  cnxn_FT1.commit()
  #Urine output data
  data_UO = round(5*rand.random(), 3)
  cursor_FT2.execute("INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp], [urine_output]) VALUES('{}', GETDATE(), {});".format(unos_id, data_UO))
  cnxn_FT2.commit()
  #Biotrend data
  data_sO2v = round(100*rand.random(), 3)
  data_hct = round(30*rand.random(), 3)
  cursor_BT.execute("INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{}', GETDATE(), {}, {});".format(unos_id, data_sO2v, data_hct))
  cnxn_BT.commit()
  
  sleep(5)
  
  lap = time() - start
