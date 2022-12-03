from os import system, name
from time import time, asctime
import pyodbc

#establish database connection
unos_id = None
server = "dtk-server.database.windows.net"
database = "perf-data"
username = "dtk_lab"
password = "data-collection1"

#define function for inputting data and re-prompting if data is invalid
def data_input(key):
	try:
		var = float(input(key))
	except:
		while 
			print("Invalid data type. Please re-enter with a float data type")
			var = float(input(key))
	return var

with pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password) as cnxn:
        with cnxn.cursor() as cursor:
		
		new_input = "Y"
		
		while (new_input == "Y"):
			time_stamp = asctime(time())
			#iStat measurements
			print("iStat Measurements:\n)
			pH = data_input("pH: ")
			PCO2 = data_input("PCO_2: ")
			PO2 = data_input("PO_2: ")
			TCO2_iStat = data_input("TCO_2: ")
			HCO3 = data_input("HCO_3: ")
			BE = data_input("BE: ")
			sO2 = data_input("sO2: ")
			Hb = data_input("Hb: ")		
			cursor.execute(f"INSERT INTO dbo.istat_t([UNOS_ID], [time_stamp], [ph], [pco2], [tco2], [hco3], [be], [so2], [hb]) VALUES({unos_id}, {time_stamp}, {pH}, {PCO2}, {PO2}, {TCO2_iStat}, {HCO3}, {BE}, {sO2}, {Hb}))
			#Piccolo measurements
			print("Piccolo Measurements:\n")
			Na = data_input("Na: ")
			K = data_input("K: ")
			TCO2_Pic = data_input("TCO_2: ")
			Cl = data_input("Cl: ")
			Glu = data_input("Glu: ")
			Ca = data_input("Ca: ")
			BUN = data_input("BUN: ")
			Cre = data_input("Cre: ")
			eGFR = data_input("eGFR: ")
			ALP = data_input("ALP: ")
			AST = data_input("AST: ")
			TBIL = data_input("TBIL: ")
			ALB = data_input("ALB: ")
		     	TP = data_input("TB: ")
	     		cursor.execute(f"INSERT INTO dbo.pic_t([UNOS_ID], [time_stamp], [Na], [K], [tco2], [Cl], [glu], [Ca], [BUN], [cre], [egfr], [alp], [ast], [tbil], [alb], [tp]) VALUES({unos_id}, {time_stamp}, {Na}, {K}, {TCO2_Pic}, {Cl}, {Glu}, {Ca}, {BUN}, {Cre}, {eGFR}, {ALP}, {AST}, {TBIL}, {ALB}, {TP}))
		     	#conditional for executing the loop again
		     	new_input = input("Enter a new set of data? (Y/N) \n")
		       
		        while (new_input != "Y" or new_input != "N"):
				print("Invalid entry. Try again.\n")
			       	new_input = input("Enter a new set of data? (Y/N) ")
				       
		       if (new_input == "Y"):
				system("cls")
		       else:
				pass
			       	
		       	
	     	
	     	
	     	
