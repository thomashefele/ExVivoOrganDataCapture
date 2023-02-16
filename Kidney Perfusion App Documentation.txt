Instructions:
- Set up an Azure SQL database for your experiment (if one is not already set up):

https://azure.microsoft.com/en-us/products/azure-sql/database/

- Ensure that your IPv4 address is added to the Azure Firewall Rules for your database (I attempted to automate this feature in the program to no avail):
  - To find your IPv4 address: 
  
    https://whatismyipaddress.com/
    
  - To add the Firewall Rule: 
  
    https://learn.microsoft.com/en-us/azure/mysql/flexible-server/how-to-manage-firewall-portal#create-a-firewall-rule-after-the-server-is-created

- Install the necessary software to connect to the database. 
  - In Windows, this software is usually pre-installed. If not, download the software from:

    https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
    
  - On Linux, ...

  *Note that installation of the driver on Mac is unreliable, thus the program should only be run on Windows or Linux.

- If scanning donor information (i.e. the "Donor information upload" option):
  - No further installations are required; download the donor history file from UNOS (https://unos.org/). Copy and paste the UNOS ID of the file into the 
  program - the program will locate and upload information from the PDF file.  
  - On the data table that appears, verify/edit any information on the table. When ready to upload, click "Upload".
  
- If uploading blood gas data (i.e. "Blood gas data upload"):
  - No further installations are required; enter the UNOS ID and submit the blood gas data. If any data is immeasurable (<> or *** on iStat; ~~~ or other 
  on Piccolo) or low/high (i.e. <N or >N), enter the data as is.
  
- If collecting data during perfusion:
  - Prior to perfusion, turn on and calibrate all sensors/instruments.
  - Windows:
    - Enter the UNOS ID and plug in all sensors according to the order indicated on the app.
    - Turn off all background apps that could hijack the COM ports for each serial port. The following guide can tell you any apps that have hijacked
    a COM port:
    
    https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGw9CAG&l=en-US

    - Once all COM ports are assigned, they will remain this way regardless of computer status. Data collection is ready to begin.
    *Note that COM ports should be assigned in ascending order according to number. If one desires to check this, they can go to "Device Manager" to check
    the COM port assignments under the tab "Ports (COM & LPT)".
  - Linux:
    - Enter the UNOS ID.
    - If the computer is off, remove all sensor USBs prior to restarting the device; if not, the computer will randomly assign USB ports. Once the computer
    is restarted, connect all sensors according to the order indicated on the app. The app is now ready for data collection.
    - If the computer is on and sensor USBs are not plugged in, connect all sensors according to the order indicated on the app. The app is now ready for 
    data collection.
    - If the computer is on and sensor USBs are plugged in from prior usage, the app is ready to commence data collection.
    
Troubleshooting:
- If a sensor is turned off or unplugged during perfusion, simply restart/reconnect the sensor. There is no need to restart or exit the program, as it is
designed to continue data collection for a sensor even if the data stream is interrupted. (NULL values are uploaded until reconnection is established.)
  - For Linux: if one or more sensors become unplugged, plug the sensors back in according to the order list. (ex. If the Bioconsole and Biotrend are
  unplugged, I will plug in the Bioconsole first) On Linux, ports are temporarily assigned; thus, removing more than one port causes the respective port
  names to be lost. Re-plugging the ports in a different order will result in different names for the ports.
- If timestamps are appearing irregularly on the app or NULL values are appearing when all sensors are connected, this is an indication that the USB ports are not connected in the right order. Do as follows:
  - If using Windows, go to Device Manager and re-assign all the COM ports in the proper ascending order. To do so, right click on the port under "Ports 
  (COM & LPT)" in Device Manager. Click on "Properties", followed by "Port Settings", and then "Advanced".
  - If using Linux, remove all sensor USBs and then re-connect the sensor USBs in the proper order.
  *Note that restarting the app is not required; the app will continue to upload NULL values until all the USBs are arranged in the proper order, at which
  point the correct values will be uploaded.
