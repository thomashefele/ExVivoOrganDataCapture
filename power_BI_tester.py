#A pseudo-data random generator for testing out the Azure database and PowerBI data visualization system.
import pyodbc, platform
import random as rand
from time import monotonic, sleep

#timer
start = monotonic() 
lap, interval, connString, unos_id = 0, 3600, "", ""
OS = platform.system()

if OS == "Linux":
    dsn = "DTKserverdatasource"
    user = "dtk_lab@dtk-server"
    password = "data-collection1"
    database = "perf-data"
    connString = "DSN={0};UID={1};PWD={2};DATABASE={3};".format(dsn,user,password,database)
elif OS == "Windows":
    driver =  "{SQL Server}"
    server = "dtk-server.database.windows.net"
    database = "perf-data"
    username = "dtk_lab"
    password = "data-collection1"
    connString = "DRIVER={0};SERVER={1};DATABASE={2};UID={3};PWD={4}".format(driver,server,database,username,password)

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
#Information for the categories below is pulled from:
#Ethnicity/race: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1447913/
eth = ["Hispanic or Latino", "White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Other Pacific Islander"]
#Gender identities: https://www.bestnotes.com/how-to-classify-gender-identity-and-track-behavioral-health-data-in-your-ehr/
gender = ["Male", "Female", "Non-binary", "Transgender male", "Transgender female", "Other", "Does not wish to disclose"]
bt = ["A", "B", "AB", "O"]

def wab():
    #For weight and bmi: https://www.cancer.org/healthy/cancer-causes/diet-physical-activity/body-weight-and-cancer-risk/adult-bmi.html
    weight = str(round(rand.uniform(91, 279), 1))
    #For age: https://www.nyp.org/transplant/organ-donation/organ-donation-facts
    age = str(rand.randint(16, 100))
    bmi = str(round(rand.uniform(19, 35), 1))
    wab_lst = [weight, age, bmi]
    
    return wab_lst

#Random data generator
while lap <= interval:  
  if lap < (interval/2):
        unos_id = "TEST_ID_1"
        cursor_don.execute("INSERT INTO dbo.organ_t([ID], [blood_type], [weight], [age], [bmi], [gender], [eth_race]) VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');".format(unos_id, rand.choice(bt), *wab(), rand.choice(gender), rand.choice(eth)))
        cnxn_don.commit()
            
  elif lap >= (interval/2):
        unos_id = "TEST_ID_2"
        cursor_don.execute("INSERT INTO dbo.organ_t([ID], [blood_type], [weight], [age], [bmi], [gender], [eth_race]) VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');".format(unos_id, rand.choice(bt), *wab(), rand.choice(gender), rand.choice(eth)))
        cnxn_don.commit()
            
  #MedTronic data
  data_AF = round(rand.random(), 3)
  data_AP = round(5*rand.random(), 3)
  rpm = round(5000*rand.random())
  cursor_MT.execute("INSERT INTO dbo.mt_t([UNOS_ID], [time_stamp], [flow], [pressure], [rpm]) VALUES('{0}', GETDATE(), {1}, {2}, {3});".format(unos_id, data_AF, data_AP, rpm))
  cnxn_MT.commit()
  #Kidney mass data
  data_KM = round(5*rand.random(), 3)
  cursor_FT1.execute("INSERT INTO dbo.km_t([UNOS_ID], [time_stamp], [kidney_mass]) VALUES('{0}', GETDATE(), {1});".format(unos_id, data_KM))
  cnxn_FT1.commit()
  #Urine output data
  data_UO = round(5*rand.random(), 3)
  cursor_FT2.execute("INSERT INTO dbo.uo_t([UNOS_ID], [time_stamp], [urine_output]) VALUES('{0}', GETDATE(), {1});".format(unos_id, data_UO))
  cnxn_FT2.commit()
  #Biotrend data
  data_sO2v = round(100*rand.random(), 3)
  data_hct = round(30*rand.random(), 3)
  cursor_BT.execute("INSERT INTO dbo.bt_t([UNOS_ID], [time_stamp], [sO2], [hct]) VALUES('{0}', GETDATE(), {1}, {2});".format(unos_id, data_sO2v, data_hct))
  cnxn_BT.commit()
  
  sleep(5)
  
  lap = monotonic() - start
