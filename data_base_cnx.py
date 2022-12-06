import pyodbc
from threading import Thread
from datetime import datetime

server = "dtk-server.database.windows.net"
database = "perf-data"
username = "dtk_lab"
password = "data-collection1"
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

with cnxn.cursor() as cursor1:
  ts_bt = datetime.now().strftime('%Y%m%d %H:%M:%S') 
  cursor1.execute(f"INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES({5}, {ts_BT}, {6}, {7});")
  cnxn.commit()
  
yn == "Y"
  
while yn == "Y":
  with cnxn.cursor() as cursor2:
    cursor2.execute(f"INSERT INTO dbo.km_t([UNOS_ID], [km]) VALUES({7}, {3});")
    cnxn.commit()
    yn = input("Yay or Nay? ")
    
def fun1():
  with cnxn.cursor() as cursor3:
    cursor3.execute(f"INSERT INTO dbo.mt_t([UNOS_ID], [flow]) VALUES({18}, {4});")
    cnxn.commit()
    
def fun2():
  with cnxn.cursor() as cursor4:
    cursor4.execute(f"INSERT INTO dbo.bt_t([UNOS_ID], [hct]) VALUES({20}, {6});")
    cnxn.commit()

thread1 = Thread(target= fun1,)
thread2 = Thread(target= fun2,)

thread1.start()
thread2.start()
thread1.join()
thread2.join()
