# *ex vivo* Organ Perfusion Continuous Data Collection Project

Last updated: 3/8/2022.
Version: 1.1

A tool for extracting, transforming, and loading (ETL) real time data on biomarkers during organ perfusions, this software can be utilized for various projects in biomedical research, such as:
- Creating digital twins of organs
- Analyzing hemodynamics and vascular leak in organs
- Whole organ isolation for studies of therapeutic effects on specific organs

The software has been developed for kidney perfusions but, as an open-source project, can be modified and customized for perfusion of any organ and myriad biometrics.

## Features:

- Available for Linux, Windows, and Mac!
- User-friendly GUI!
- Backup system stores data on CSV files in case connection to database is not established (such as internet loss, lack of firewall access, or lack of SQL driver)
- Data mining with PDF scanner automates the process of finding pertinent donor medical history. The user can then check and edit donor information prior to storing in database.
- User input for blood gas measurements and medications; perfusate, urine, and biopsy samples.
- Real time data collection of biomarkers pertinent to hemodynamics and vascular leak, such as:
  - Arterial pressure
  - Arterial flow
  - Arterial and venous oxygen saturation
  - Hematocrit
  - Organ mass
  - Urine production
- Alarms to warn if a sensor has powered off/become disconnected
- Real time data visualization provided by PowerBI

## Start Up:

Prior to commencing the GUI, the software will conduct unit tests on the database connection and the backup system:

<img width="1440" alt="Start Up" src="https://user-images.githubusercontent.com/116929892/224196929-1d694a20-6cb6-4178-a491-9e996c21c016.png">

As shown above, the results of the upload test will outline steps that can be taken to resolve each respective issue. The database connection requires one to have an Azure database, firewall access, an SQL driver that can connect to the database, and a private internet connection. The section "Establishing Azure Database Connection (Optional)" contains information on how to setup and connect to an Azure database.

The backup CSV system works as intended on Mac and Linux, but has mixed success on Windows if the OS is Windows 11:

          https://windowsreport.com/windows-11-python-permission-denied/
  
The issue is not due to the software but rather is strictly a Windows issue due to permissions in the file directory of the OS system. The link above is useful in remedying this issue.

The database upload and backup CSV uploads are separate and hence do not interfere with one another. Thus, if one is unable to connect to the database, they can still use the software in an offline-manner through the backup CSV system (the converse also holds as well).

## Navigating the GUI:

The GUI of the software appears as follows:

![GUI Main](https://user-images.githubusercontent.com/116929892/223634508-e9fe156e-4a5b-46e3-b220-80d16acdb9f4.png)

To use, simply select an option, enter the UNOS ID (or another identifier), and choose if the trial is a control or experimental. There are four options from which to choose:
- Donor information upload
- Perfusate data and medications
- Sensor data collection
- Samples

Due to the runtime complexity of each individual option, the app is designed to run only one feature at a time. Want to choose a different option? Simply click "Restart"! The app will save the UNOS ID so you can choose a new task without the redundancy of having to enter the UNOS ID each time.

## Donor Information Upload:
  
Enter a UNOS ID and the software will find and mine data from the respective file on your computer: 
  
![DI1](https://user-images.githubusercontent.com/116929892/223640050-e704a6c0-d636-4ac1-89b8-504338602290.png)
  
  *Note: for donor privacy, the above is a screenshot of a non-existent file to which "dummy" data has been added manually.
  
If the data does not appear correct or data is missing, one can edit by double clicking on a cell or by adding a column via right click:
  
![DI2](https://user-images.githubusercontent.com/116929892/223640071-2405daeb-8408-4fc3-bae8-e62cd3f95bec.png)

![DI3](https://user-images.githubusercontent.com/116929892/223640093-e17365f7-7e4d-418e-ad93-91bb1c6cd3e3.png)
  
## Perfusate Data and Medications:

Take output from iStat and Piccolo analyzers, enter into the app, and upload! Easy as can be!
  
<img width="1440" alt="Perf" src="https://user-images.githubusercontent.com/116929892/223634550-d04d1168-8eeb-44ac-ae02-34b92a298ebc.png">

The recording of medications administered allows one to determine whether or not changes in the pathophysiology of the organ (as visualized by the sensor data collected) can be ascribed to the medication (in conjunction with the data collected on control organs).
  
## Sensor Data Collection:
  
To start sensor data collection, follow the steps below:
- Ensure each sensor is on and properly calibrated
- Connect the USB cables for each driver to the computer according to the order on the GUI:

  ![Sensors](https://user-images.githubusercontent.com/116929892/223640132-2e63cda4-4591-4df9-b799-eafeec0e83fc.png)
    
- Once all sensors are connected, click "Click to check port status" followed by "Start Data Collection". All done!
  
  ![Sensors 2](https://user-images.githubusercontent.com/116929892/223640169-f2813a53-d90b-42fe-b374-86cded7b3b08.png)
    
- If connected to a cloud database (see "Establishing Database Connection" below), the data will be uploaded to the database automatically. If not, the data can be retrieved from CSV files that can be found on the computer:
    
    - Donor information: [id]_donor_info.csv
    - Medications: [id]_meds.csv
    - iStat and Piccolo data: [id]_[control_or_experimental]_istat.csv, [id]_pic.csv
    - Arterial flow and pressure: [id]_[control_or_experimental]_mt_data.csv
    - Venous oxygen saturation and hematocrit: [id]_[control_or_experimental]_bt_data.csv
    - Kidney mass: [id]_[control_or_experimental]_km_data.csv
    - Urine output: [id]_[control_or_experimental]_uo_data.csv
    
- The time stamps indicate to you the last time data was uploaded from each respective sensor. Each time stamp should update every ~5 seconds.
- To restart or exit from data collection, make sure to click "Stop Data Collection" first and wait for time stamps to stop updating. Afterwards, "Restart" or "Exit" may be clicked.
    
## Samples:

The software is also designed so that unique identifiers of biological samples (such as barcodes) may be recorded and uploaded to the database:

![Samples](https://user-images.githubusercontent.com/116929892/223641354-14c9c2df-3a93-47bc-8812-80169e7491fa.png)

The resulting record of samples can also be used to corroborate changes in the sensor data, such as a decrease in urine mass/introduction of noise due to a collection of urine sampling.
    
## Data Visualization with PowerBI:
    
If using the Azure database, PowerBI can pull data from the database and display it to provide users with a realtime visualization of what is happening during the perfusion. In addition, the AI in PowerBI allows one to ask questions about specific perfusion metrics to gain powerful insights to organ performance!

  <img width="658" alt="PowerBI" src="https://user-images.githubusercontent.com/116929892/220245423-9167dbdf-86d0-4704-ad37-6ca7920c3ac8.png">
  
  *Note: for donor privacy, the above is a screenshot of pseudo-data produced by the *power_BI_tester.py* program.

## Establishing Azure Database Connection (Optional):
  
Although the program has been designed to be user-friendly and flexible in use, the most ideal use of the software is when coupled with Azure. To setup an Azure database and connection, follow the instructions below:
  
  - Set up an Azure SQL database for your experiment (if one is not already set up):

          https://azure.microsoft.com/en-us/products/azure-sql/database/

  - Ensure that your IPv4 address is added to the Azure Firewall Rules for your database:
    - To find your IPv4 address: 
  
          https://whatismyipaddress.com/
    
    - To add the firewall rule: 
  
          https://learn.microsoft.com/en-us/azure/mysql/flexible-server/how-to-manage-firewall-portal#create-a-firewall-rule-after-the-server-is-created

- Install the necessary software to connect to the database. 
  - In Windows, this software is usually pre-installed. If not, download the software from:

          https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
    
  - On Linux:
  
          https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=alpine18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline
  
  - On Mac:
  
          https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16
  
  There are a multitude of alternative drivers for Mac and Linux in addition to the above.
  
- Ensure that your wifi is a private network. Public networks will not work for uploading data to Azure. (Although data can still be written to CSV files on the backup system.)

## Troubleshooting:

Q: The time stamp(s) are not appearing/have stopped updating What is happening?

A: There are three known causes of this:

  - If the time stamps are not appearing, this means that the database connection was never established and that the backup system is not working. The software is designed so that if an upload is made to the database or to a backup CSV file, the time stamp updates. Likewise, for other data if an upload is made, a "Data successfully saved!" message is reported. For database connection, see "Establishing Azure Database Connection (Optional)".

    The backup system code itself has no errors and works as intended on Mac and Linux; however, mixed success has been encountered with the system on Windows. On some Windows devices, the system works as intended; on others, an "PermissionError: [Errno 13] Permission denied" is raised. This is strictly a Windows issue due to permissions in the file directory of the OS system. A useful article on circumventing this:

          https://windowsreport.com/windows-11-python-permission-denied/

    If none of the solutions proposed above work, the code can be run from a Jupyter notebook (or other notebook) and the filewriting feature will work as     intended. The backup CSV files can be found in the Jupyter directory and then downloaded to the Windows device.

- On Linux, a unique and very rare startup error ("OSError: errno 5 input/output error") can appear if the initialization with one of the serial port drivers is not successful. This is not a software issue but rather an issue between the driver and the hardware in making a connection. Stop the data collection, click "Exit" and restart the program. (Do NOT just click "Restart".)

- The internet connection has abruptly been broken. See "We have lost internet connection..." question below.

Please note that the software is designed to upload to the database and the backup CSV files separately. As such, if an unforeseen error occurs with one, it will not affect the performance of the other and vice-versa.

Q: The time stamp(s) are appearing irregularly! What can be done?

A: This is an indicator that the USB ports have not been plugged in properly. Follow the steps for each OS below:

 - Linux and Mac: Unplug ALL USB ports and re-connect them according to the proper order stated on the GUI.      
 - Windows: The COM port numbers must be changed so that the order matches that stated on the GUI. A most excellent guide for how to do this:

          https://kb.plugable.com/serial-adapter/how-to-change-the-com-port-for-a-usb-serial-adapter-on-windows-7,-8,-81,-and-10

On Windows, another issue that may occur is that a background app may be hijacking the COM ports. Another most excellent guide for how to check:

          https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGw9CAG&l=en-US

After finding the app that is hijacking the COM ports, one can quit or turn off that app.

Q: We have lost internet connection during perfusion! Is our data being lost?

A: The software has a backup feature that writes the data to local CSV files during the perfusion. If there is a connection issue during perfusion         (internet or otherwise), data will continue to be written to the CSV files, which can then be uploaded to the database post-perfusion. That being         said, the backup feature is not foolproof: rarely, if the internet connection is lost abruptly, the timestamp(s) will cease to update/not appear,         indicating that data transfer is no longer occuring. In this case, exit out of the program and re-open. (Do NOT simply click "Restart".)

Q: USB port(s) have powered off/become disconnected during perfusion! What should we do?

A: The software has been designed to account for such things. The data transfer will continue until the issue has been resolved, with NULL values         being uploaded in place of the usual values. If a sensor is off, simply turn the sensor back on. If a sensor is disconnected, simply reconnect it.         (Note that if multiple sensors become unplugged, they must be plugged back in according to the order stated on the GUI.)

To report other unforeseen issues that may arise, please contact dtk.yale@gmail.com
