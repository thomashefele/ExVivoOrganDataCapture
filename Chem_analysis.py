from time import time
import pyodbc

#establish database connection
unos_id = None
server = "dtk-server.database.windows.net"
database = "perf-data"
username = "dtk_lab"
password = "data-collection1"
with pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password) as cnxn:
        with cnxn.cursor() as cursor:
		while (new_input == "Y"):
			time_stamp = time()
			#iStat measurements
			print("iStat Measurements:\n)
			pH = float(input("pH: "))
			PCO2 = float(input("PCO_2: "))
			PO2 = float(input("PO_2: "))
			TCO2_iStat = float(input("TCO_2: "))
			HCO3 = float(input("HCO_3: "))
			BE = float(input("BE: "))
			sO2 = float(input("sO2: "))
			Hb = float(input("Hb: "))		
			cursor.execute(f"INSERT INTO dbo.istat_t([UNOS_ID], [time_stamp], [ph], [pco2], [tco2], [hco3], [be], [so2], [hb]) VALUES({unos_id}, {time_stamp}, {pH}, {PCO2}, {PO2}, {TCO2_iStat}, {HCO3}, {BE}, {sO2}, {Hb}))
			#Piccolo measurements
			print("Piccolo Measurements:\n")
			Na = float(input("Na: "))
			K = float(input("K: "))
			TCO2_Pic = float(input("TCO_2: "))
			Cl = float(input("Cl: "))
			Glu = float(input("Glu: "))
			Ca = float(input("Ca: "))
			BUN = float(input("BUN: "))
			Cre = float(input("Cre: "))
			eGFR = float(input("eGFR: "))
			ALP = float(input("ALP: "))
			AST = float(input("AST: "))
			TBIL = float(input("TBIL: "))
			ALB = float(input("ALB: "))
		     	TP = float(input("TB: "))
	     		cursor.execute(f"INSERT INTO dbo.pic_t([UNOS_ID], [time_stamp], [Na], [K], [tco2], [Cl], [glu], [Ca], [BUN], [cre], [egfr], [alp], [ast], [tbil], [alb], [tp]) VALUES({unos_id}, {time_stamp}, {Na}, {K}, {TCO2_Pic}, {Cl}, {Glu}, {Ca}, {BUN}, {Cre}, {eGFR}, {ALP}, {AST}, {TBIL}, {ALB}, {TP}))
		     	#conditional for executing the loop again
		     	new_input = input("Enter a new set of data? (Y/N)")
		       	
	     	
	     	
	     	
