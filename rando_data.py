import pyodbc
import random as rand

#timer
start = time() 
lap = 0
interval = 300

#Establish database connection
dsn = 'DTKserverdatasource'
user = 'dtk_lab@dtk-server'
password = 'data-collection1'
database = 'perf-data'
connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)

cnxn_MT =  pyodbc.connect(connString)
cursor_MT = cnxn_MT.cursor()
cnxn_BT =  pyodbc.connect(connString)
cursor_BT = cnxn_BT.cursor()
cnxn_FT1 =  pyodbc.connect(connString)
cursor_FT1 = cnxn_FT1.cursor()
cnxn_FT2 =  pyodbc.connect(connString)
cursor_FT2 = cnxn_FT2.cursor()

#data generator
while lap <= interval:
 
  unos_id = "TEST_ID"
  
  #MedTronic data
  data_AF = round(rand.random(), 3)
  data_AP = round(5*rand.random(), 3)
  cursor_MT.execute("INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure]) VALUES('{}', GETDATE(), {}, {});".format(unos_id, data_AF, data_AP)))
  cnxn_MT.commit()
  #Kidney mass data
  data_KM = round(5*rand.random(), 3)
  cursor_FT1.execute("INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{}', GETDATE(), {});".format(unos_id, data_KM))
  cnxn_FT1.commit()
  #Urine output data
  data_UO = round(5*rand.random(), 3)
  cursor_FT2.execute("INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{}', GETDATE(), {});".format(unos_id, data_UO))
  cnxn_FT2.commit()
  #Biotrend data
  data_sO2 = round(100*rand.random(), 3)
  data_hct = round(30*rand.random(), 3)
  cursor_BT.execute("INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{}', GETDATE(), {}, {});".format(unos_id, data_sO2v, data_hct))
  cnxn_BT.commit()
  
  sleep(5)
  
  lap = time() - start
