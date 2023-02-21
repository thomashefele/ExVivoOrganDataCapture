# DTK Data Collection Project
Contributors: Alborz Feizi, Kat Nurminsky, Thomas Hefele

A tool for extracting, transforming, and loading (ETL) real time data on biomarkers during kidney perfusions, this software can be utilized for various projects in healthcare, such as:
- Creating digital twins of organs
- Analyzing hemodynamics and vascular leak in organs

Features:

- Available for Linux, Windows, and Mac!
- User-friendly GUI!
- Backup system stores data on CSV files in case connection to database is broken (such as internet loss, lack of firewall access, or lack of SQL driver)
- PDF scanner will find and extract pertinent donor information. User can check and edit donor information prior to storing in database.
- User input for blood gas measurements
- Real time data collection of biomarkers pertinent to hemodynamics and vascular leak, such as:
  - Arterial pressure
  - Arterial flow
  - Venous oxygen saturation
  - Hematocrit
  - Organ mass
  - Urine production
- Alarms to warn if a sensor has powered off/become disconnected
- Real time data visualization provided by PowerBI

Navigating the GUI:

The GUI of the software appears as follows:

![GUI Main](https://user-images.githubusercontent.com/116929892/220244767-1b087a14-031e-4603-9dd4-3252978b9c21.png)

To use, simply select an option and enter the UNOS ID (or another identifier) into the app. There are three options from which to choose:
- Donor Information Upload
- Blood Gas Data Upload
- Sensor Data Collection

The app is designed to run only one feature at a time. Want to choose a different option or entered the wrong ID? Simply click "Restart"!

Donor Information Upload:
  
Enter a UNOS ID and the software will find and mine data from the respective file on your computer: 
  
![DI_1](https://user-images.githubusercontent.com/116929892/220244880-387d45df-9a70-4b56-9a12-6023163dd293.png)
  
  *Note: for donor privacy, the above is a screenshot of a non-existent file, to which "dummy" data has been added manually
  
If the data does not appear correct or data is missing, one can edit by double clicking on a cell or by adding a column via right click:
  
![DI_2](https://user-images.githubusercontent.com/116929892/220244909-f5e184fd-b33e-4856-9c98-f82e2bfe120a.png)

![DI_3](https://user-images.githubusercontent.com/116929892/220244921-1d97af0c-0d2f-4d4b-a54c-86cabbe9192e.png)
  
Blood Gas Data Upload:

Take output from iStat and Piccolo analyzers, enter into the app, and upload! Easy as can be!
  
![BG](https://user-images.githubusercontent.com/116929892/220245002-b4d3d7a4-b201-4a3b-8514-b3906e1af30b.png)
  
Sensor Data Collection:
  
To start sensor data collection, follow the steps below:
- Ensure each sensor is on and properly calibrated
- Connect the USB cables for each driver to the computer according to the order on the GUI:

  ![Driver_order](https://user-images.githubusercontent.com/116929892/220245035-19556eca-5424-44ef-bb6c-e3e0f25562e8.png)
    
- Once all sensors are connected, click "Click to check port status" followed by "Start data collection". All done!
  
  ![Data_stamp_pic](https://user-images.githubusercontent.com/116929892/220245088-0e519bde-188c-45d3-9a0b-b1b669d2ede7.png)
    
- If connected to a cloud database (see "Establishing Database Connection" below), the data will be uploaded to the database automatically. If not, the data can be retreived from csv files that can be found on the computer:
    
    - Donor information: donor_info.csv
    - iStat and Piccolo data: istat.csv, pic.csv
    - Arterial flow and pressure: mt_data.csv
    - Venous oxygen saturation and hematocrit: bt_data.csv
    - Kidney mass: km_data.csv
    - Urine output: uo_data.csv
    
- The time stamps indicate to you the last time data was uploaded from each respective sensor. Each time stamp should update every ~5 seconds.
- To restart or exit from data collection, make sure to click "Stop Data Collection" first and wait for time stamps to stop updating. Afterwards, "Restart" or "Exit" may be clicked.
    
- Troubleshooting Data Collection:
    
    Q: USB port(s) have powered off/become disconnected during perfusion! What should we do?
    
    A: The software has been designed to account for such things. The data transfer will continue until the issue has been resolved, with NULL values         being uploaded in place of the usual values. If a sensor is off, simply turn the sensor back on. If a sensor is disconnected, simply reconnect it.         (Note that if multiple sensors become unplugged, they must be plugged back in according to the order stated on the GUI.)    
    
    Q: We have lost internet connection during perfusion! Is our data being lost?
    
    A: The software has a backup feature that writes the data to local csv files during the perfusion. If there is a connection issue during perfusion, 
    data will continue to be written to the csv files, which can then be uploaded to the database post-perfusion. That being said, the backup feature is       not foolproof. Rarely, if the internet connection is lost abruptly, the timestamp(s) will cease to update/not appear, indicating that data transfer is     no longer occuring. In this case, exit out of the program and re-open. (Do NOT simply click "Restart".)
    
    Q: The time stamp(s) are appearing irregularly!
    
    A: This is an indicator that the USB ports have not been plugged in properly. Follow the steps for each OS below:
      - Linux and Mac: Unplug ALL USB ports and re-connect them according to the proper order stated on the GUI.
      - Windows: The COM port numbers must be changed so that the order matches that stated on the GUI. A most excellent guide for how to do this:
    
              https://kb.plugable.com/serial-adapter/how-to-change-the-com-port-for-a-usb-serial-adapter-on-windows-7,-8,-81,-and-10
    
    On Windows, another issue that may occur is that a background app may be hijacking the COM ports. 
   
              https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGw9CAG&l=en-US
    
    After finding the app that is hijacking the COM ports, one can quit or turn off that app.
    
    To report unforeseen issues that may arise, please contact dtk.yale@gmail.com
    
Data Visualization with PowerBI:
    
If using the Azure database, PowerBI can pull data from the database and display it to provide users with a realtime visualization of what is happening during the perfusion. In addition, the AI in PowerBI allows one to ask questions about specific perfusion metrics to gain powerful insights to organ performance!

<img width="658" alt="PowerBI" src="https://user-images.githubusercontent.com/116929892/220245423-9167dbdf-86d0-4704-ad37-6ca7920c3ac8.png">

Establishing Azure Database Connection (Optional):
  
Although the program has been designed to be user-friendly and flexible in use, the most ideal use of the software is when coupled with Azure. To setup an Azure database and connection, follow the instructions below:
  
  - Set up an Azure SQL database for your experiment (if one is not already set up):

          https://azure.microsoft.com/en-us/products/azure-sql/database/

  - Ensure that your IPv4 address is added to the Azure Firewall Rules for your database:
    - To find your IPv4 address: 
  
          https://whatismyipaddress.com/
    
  - To add the Firewall Rule: 
  
          https://learn.microsoft.com/en-us/azure/mysql/flexible-server/how-to-manage-firewall-portal#create-a-firewall-rule-after-the-server-is-created

- Install the necessary software to connect to the database. 
  - In Windows, this software is usually pre-installed. If not, download the software from:

          https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
    
  - On Linux:
  
          https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline
  
  - On Mac:
  
          https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16
