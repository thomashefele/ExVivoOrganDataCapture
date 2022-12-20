import pyodbc
import random as rand
from time import time

#timer
start = time() 
lap = 0
interval = 300

#connections to Azure
#establish database connection
server = "dtk-server.database.windows.net"
database = "perf-data"
username = "dtk_lab"
password = "data-collection1"

cnxn_MT =  pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor_MT = cnxn_MT.cursor()
cnxn_BT =  pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor_BT = cnxn_BT.cursor()
cnxn_FT1 =  pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor_FT1 = cnxn_FT1.cursor()
cnxn_FT2 =  pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor_FT2 = cnxn_FT2.cursor()

#data generator
while lap <= interval:
 
  unos_id = "1234"
  ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
  #MedTronic data
  data_AF = round(rand.random(), 3)
  data_AP = round(5*rand.random(), 3)
  cursor_MT.execute(f"INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure]) VALUES('{unos_id}', '{ts}', {data_AF}, {data_AP});")
  cnxn_MT.commit()
  #Kidney mass data
  data_KM = round(5*rand.random(), 3)
  cursor_FT1.execute(f"INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{unos_id}', '{ts}', {data_KM});")
  cnxn_FT1.commit()
  #Urine output data
  data_UO = round(5*rand.random(), 3)
  cursor_FT2.execute(f"INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp], [urine_output]) VALUES('{unos_id}', '{ts}', {data_UO});")
  cnxn_FT2.commit()
  #Biotrend data
  data_sO2 = round(100*rand.random(), 3)
  data_hct = round(30*rand.random(), 3)
  cursor_BT.execute(f"INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{unos_id}', '{ts}', {data_sO2}, {data_hct});")
  cnxn_BT.commit()
  
  sleep(5)
  
  lap = time() - start

 


