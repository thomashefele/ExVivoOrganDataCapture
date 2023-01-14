from tkinter import *, ttk
import pyodbc, os, platform, sys

#Establish and preliminaries for app database connection
connString = ""
OS = platform.system()
if OS == "Linux":
    if os.environ.get('DISPLAY','') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')
        
    dsn = 'DTKserverdatasource'
    user = 'dtk_lab@dtk-server'
    password = 'data-collection1'
    database = 'perf-data'
    connString = 'DSN={0};UID={1};PWD={2};DATABASE={3};'.format(dsn,user,password,database)
        
elif OS == "Windows":
    server = "dtk-server.database.windows.net"
    database = "perf-data"
    username = "dtk_lab"
    password = "data-collection1"
    connString = "DRIVER={SQL Server};SERVER={0};DATABASE={1};UID={2};PWD={3}".format(server,database,username,password)

#The code below initializes the windows and tabs for the app. 
app = Tk()
app.title("Kidney Donor Information")
app.geometry("350x525")
