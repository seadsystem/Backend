spectrogram.py

Description: 

(1) Takes in database data, parses, and create a spectrogram data from the SEAD plug with old server and new server in one folder

To run this program. Type:

python spectrogram.py [input directory] [outfolder][sensor ID's for old server] 

For example: python spectrogram.py directory/to/files/ ./outfolder/ 11 12 13

usage: spectrogram.py [input folder path dir] [output folder path] [ac_id] [wattage_id] [temperature_id]

Note: data from the new server should generate automatically if your data from new server and old server are in one folder

harmonics_3d.py

Description:

(1) Takes in .xlsx files from directory, parses, and creates 3-D graph of PA1000 formatted data

usage: harmonics_3d.py [file directory input] [file directory output]

Note: this is just testing with given data from Ali's. This program is not really related to our project 
