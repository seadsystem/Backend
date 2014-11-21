#Most Current Documentation Added!
#How To Gather SEAD Plug Raw Data From MySQL

##MySQL Setup/Connection 
You will need a MySQL GUI tool to access and download SEAD plug in csv data format. 
MySQL Workbench is one such tool, free for download here: <a>http://dev.mysql.com/downloads/workbench/</a> </br>
Once downloaded, you create a connection to the database with the folllwing parameters:
</br>- Connection Name: (You may choose whatever name you wish)
</br>- Use standard TCP/IP connection method.
</br>- Hostname: sead.systems
</br>- Port: 3306
</br>- Username: root
</br>- Password: teammantey
</br>- Default Schema (Optional): shempserver </br></br>

###This is a screenshot of a valid MySQL database connection.
</br>![Alt screenshot](/Users/Quintin/Desktop/mysql_connection.png)</br>

Press the "Test Connection" button to verify that the parameters are correct, then close the window.</br>
Open the connection to the database by double clicking on the connection you just created.</br>

###MySQL Workbench successfull connection 
![Alt GUI](/Users/Quintin/Desktop/img1.png)</br>

## Data Gathering
### Repeat the preceeding steps every time you gather data for a new device.
To clear what is currently in the data landing zone table issue the following MySQL command. </br>
<b>WARNING: This will clear all the existing data in the data_raw table, so make sure you have gathered the necessary information from it.</b>

    TRUNCATE TABLE shempserver.data_raw;

To execute a query, hit the lightning bolt on the far left without the magnifying glass or "I" in front of it.

![Alt truncate](/Users/Quintin/Desktop/truncate.png)

Plug in your appliance into the SEAD Plug, making sure all network connections are established between the plug and the server. (4 Lights should be on)</br>
Turn appliance on and off for a minute as during standard data gathering with the PA1000.</br>
The table will now have the data from the appliance you just gathered.</br>
Retrieve data from table by executing the following query:

    SELECT * FROM shempserver.data_raw LIMIT 1000000;

Hit the floppy disk button on the result set table to export data as CSV file.

![Alt export](/Users/Quintin/Desktop/export.png)




    

