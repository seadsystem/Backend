#For numerical analysis                                                 
import numpy as np                                                            
import math
                                                                       
#For visualization                                                      
import matplotlib.pyplot as pyp                                         
                                                                        
#For manipulating command-line arguments                                
import sys                                                              
                                                                        
#For handling files                                                      
import os 
                                                              
#For using regular expressions                                          
import re  



def import_and_trim():
	Currents = []

	#Try to open source file for reading                                    
	filename = "export.csv"                             
	if os.path.isfile(filename):                                               
		with open(filename) as f:
			#Check the first element of the first line.
			#if it's "sensor_id", it's the old format
			#if it's "1", it's the new format

			line = f.readline().split(',')

			#New format
			if len(line) == 2:
				#discard first one
				for line in f:
					line = line.split(',')
					Currents.append(line[1])
	else:
		print "Analysis: cannot open file:", filename

def produce_mean_normalized_power_spectrum(blocklist):
	#question: mean then normalize, or normalized then mean?
	#doesn't matter because multiplication commutes

	#units are in square amps
	#here's why:
	#original was in amps
	#take ft (not fft)
	#break up original into frequency components
	#view from frequency perspective
	#frequency components are in amps
	#take mod square using absolute
	#mod square(a + bi) = a^2 + b^2
	#units are now in square amps per hz
	#integrate it in piecese from a to a + blockwidth
	#now you have units of amps sqared
	#put those in an array
	#oh yeah
	#so now we have a power spectrum for an amp signal (odd sounding)
	#in amps squared
	print len(blocklist)
	exit()

	#Produce power spectrum, sum                                 
	power_spectrum = np.square(np.absolute(np.fft.rfft(blocklist[0])))
	sum_power_spectrum = power_spectrum
	for i in xrange(1, len(blocklist)):
		power_spectrum = np.square(np.absolute(np.fft.rfft(blocklist[i])))
		sum_power_spectrum = np.add(sum_power_spectrum, power_spectrum)

	#Take integral
	total_sq_amps = 0.0
	for i in xrange(0, len(sum_power_spectrum)):
		total_sq_amps += sum_power_spectrum[i]

	#Normalize by total amps measured
	normalized_power_spectrum = sum_power_spectrum * (1/total_sq_amps)

	#Finish taking mean
	mean_normalized_spectrum = normalized_power_spectrum / len(blocklist)

	return mean_normalized_spectrum

def produce_blocklist():
	blocklist = []
	data_length = len(Currents) 
	i = 0

	while i < data_length:
		if i + 200 > len(Currents):                                       
			break   
		blocklist.append(Currents[i:i+blockwidth])                        
		i += blockwidth 

	return blocklist

def display(spectrum):
	template = np.ones(len(spectrum))

	#Get the plot ready and label the axes
	pyp.plot(spectrum)
	max_range = int(math.ceil(np.amax(spectrum) / standard_deviation))
	for i in xrange(0, max_range):
		pyp.plot(template * (mean + i * standard_deviation))
	pyp.xlabel('Units?')
	pyp.ylabel('Amps Squared')    
	pyp.title('Mean Normalized Power Spectrum')
	if 'V' in Options:
		pyp.show()
	if 'v' in Options:
		tokens = sys.argv[-1].split('.')
		filename = tokens[0] + ".png"
		input = ''
		if os.path.isfile(filename):
			input = raw_input("Error: Plot file already exists! Overwrite? (y/n)\n")
			while input != 'y' and input != 'n':
				input = raw_input("Please enter either \'y\' or \'n\'.\n")
			if input == 'y':
				pyp.savefig(filename) 
			else:
				print "Plot not written."
		else:
			pyp.savefig(filename) 

Currents = []

import_and_trim()
Blocklist = produce_blocklist()
Spectrum = produce_mean_normalized_power_spectrum(Blocklist)
display(Spectrum)