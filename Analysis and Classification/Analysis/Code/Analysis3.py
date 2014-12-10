#!/usr/bin/env python3

##
# Analysis3.py
#
# Authors: Vincent Steffens
#          Lanjing Zhang 
#          Kevin Doyle
#          Ian Gudger <igudger@ucsc.edu>
#
# Date:   10 December 2014
#
# Produces mean power spectra from raw SEAD plug current 
# data, normalized by time and current. 
# Outputs spectrua in numpy arrays to stdout or a text 
# file, each array element on a line.
##  

#For numerical analysis                                                 
import numpy as np                                                            
import math

#For automatic feature extraction and classification
from sklearn import neighbors
import pickle

#For visualization                                                      
import matplotlib.pyplot as pyp                                         
                                                                        
#For manipulating command-line arguments                                
import sys                                                              
                                                                        
#For handling files                                                      
import os 
                                                              
#For using regular expressions                                          
import re

def init():
	""" 
	Starts the program. Verifies proper input, handles user-specified options.
	To add:
	* Verify that the input file exists
	"""

	#Check for proper number of arguments, die if necessary
	#max args = 2 + number of valid options, one for program name, one for 
	#input file name.
	max_args = 10
	if len(sys.argv) < 2:
		print("Usage: Analysis.py [-cfhpvVw] source_file")
		print("Call with -h for help")
		sys.exit(-1)
	if len(sys.argv) > max_args:
		print("Usage: Analysis.py [-cfhpvVw] source_file")
		print("Call with -h for help")
		sys.exit(-2)

	#handle calling with only Analysis.py -h
	if sys.argv[1] == '-h':
		print_help()
		exit()

	#Check for options. Break the option area of argv into a list of 
	#characters. Make a list of those that are valid, and a list of 
	#those that aren't. Let the user know if they endered an invalid 
	#option.

	#When adding options, be sure to add a description to the -h section
	#below
	#for reference
	#c: classify
	#d: debug
	#f: fragmented data (now obselete)
	#h: help
	#p: print spectrum to stdout
	#v: save plot of spectrum
	#V: display plot of spectrum
	#w: write spectrum to file
	#r: record spectrum and device type into scikit learn
	valid_options = 'cdfhpvVwr'
	alleged_options = list(set(''.join(sys.argv[1:2])))
	options = [x for x in alleged_options if re.search(x, valid_options)]
	non_options = [x for x in alleged_options if x not in options and x != '-']

	for i in non_options:
		print("Ignoring invalid option: \'%s\'" % (i))

	return options

'''
This is probably obselete
def import_and_trim(currents):
	"""
	Handles data input in various formats. Data is gathered from the db.
	This may now be obselete.
	"""

	#Try to open source file for reading  
	#we'll be taking data as a 1-d array                                  
	filename = sys.argv[len(sys.argv) - 1]                                  
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
					currents.append(line[1])
			elif line[0] == '1':
				if line[1] == 'I':
					currents.append(line[3])
				for line in f:
					line = line.split(',')
					if line[1] == 'I':
						currents.append(line[2])
			else:
				for line in f:
					line = re.split(',|\t', line)
					if int(line[0]) in amp_ids:
						currents.append(line[1])
	else:
		print("Analysis: cannot open file:", filename)
      
	#Convert currents to milliamps                                                                 
	#this scale factor is currently not calibrated
	currents = [ 27*float(x)/1000 for x in currents ] 

	return Currents
'''

def produce_blocklist(blockwidth):
	"""
	Formats the data into timesteps of a given width. This is necessary to 
	force the fft to produce components within a regular range of frequencies.
	"""

	blocklist = []

	data_length = len(Currents) 
	i = 0
	while i < data_length:
		if i + blockwidth > len(Currents):                                       
			break   
		blocklist.append(Currents[i:i+blockwidth])                        
		i += blockwidth 

	return blocklist

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

	#Produce power spectrum, sum                                 
	power_spectrum = np.square(np.absolute(np.fft.rfft(blocklist[0])))
	sum_power_spectrum = power_spectrum
	for i in range(1, len(blocklist)):
		power_spectrum = np.square(np.absolute(np.fft.rfft(blocklist[i])))
		sum_power_spectrum = np.add(sum_power_spectrum, power_spectrum)

	#Take integral
	total_sq_amps = 0.0
	for i in range(0, len(sum_power_spectrum)):
		total_sq_amps += sum_power_spectrum[i]

	#Normalize by total amps measured
	normalized_power_spectrum = sum_power_spectrum * (1/total_sq_amps)

	#Finish taking mean
	mean_normalized_spectrum = normalized_power_spectrum / len(blocklist)

	return mean_normalized_spectrum

def display(spectrum):
	template = np.ones(len(spectrum))

	#Get the plot ready and label the axes
	pyp.plot(spectrum)
	max_range = int(math.ceil(np.amax(spectrum) / standard_deviation))
	for i in range(0, max_range):
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
			input = input("Error: Plot file already exists! Overwrite? (y/n)\n")
			while input != 'y' and input != 'n':
				input = input("Please enter either \'y\' or \'n\'.\n")
			if input == 'y':
				pyp.savefig(filename) 
			else:
				print("Plot not written.")
		else:
			pyp.savefig(filename) 

def write_output():
	tokens = sys.argv[-1].split('.')
	filename = tokens[0] + ".txt"
	#If a file with the same name already exists,
	#check before overwriting and skip if necessary
	if os.path.isfile(filename):
		input = input("Error: Output file already exists! Overwrite? (y/n) : ")
		while input != 'y' and input != 'n':
			input = input("Please enter either \'y\' or \'n\'.\n")
		if input == 'n':
			print("Writing skipped.")
			return

	#Write
	out = open(filename, 'w')
	for element in Spectrum:
		out.write(str(element) + ",")
	out.close()

def print_help():
	print("\nAnalysis.py.")
	print("Used to produce a mean power spectrum of raw SEAD plug current data, normalized by total current")
	print("For recording, at least 5 inputs per category is needed (hard-coded), but ideally more")
	print("\nCall using this syntax:")
	print("$ python Analysis.py [-fhpvVwr] [device type] [input file]")
	print("")
	print("Input: Raw, 4-column SEAD plug data")
	print("Output: Either or both of:")
	print("1. Numpy array printed to stdout.")
	print("2. Spectrum written to text file.")
	print("\nOptions may be arranged in any order, and in any number of groups")
	print("")
	print("-f:\t Fragmented data. This handles gaps in the data.")
	print("-h:\t Help. Display this message.")
	print("-p:\t Print. Print numpy array containing spectrum to terminal.")
	print("-V:\t View. Display plot of spectrum, with the mean and multiples of the standard deviation.")
	print("-v:\t Visualize. Print plot to file.")
	print("-w:\t Write. Write spectrum to file, each array element on its own line")
	print("-r:\t Record. Record signature and device type into scikit-learn; note that it overwrites existing clf.p")

	print("\nExamples:")
	print("1: Handle fragmented data, view plot, write spectrum to file")
	print("   python Analysis.py -vfw 1_raw.csv")
	print("   python Analysis.py -f -wv 1_raw.csv")
	print("2: View plot of spectrum")
	print("   python Analysis.py -V 1_raw.csv")

def count_inputs(target):#makes sure that device count >=2; inputs per device >=minimum
	minimum = 5
	makeclf = True # if True make classifier
	target_list = target.tolist() #target is the array containing device types
	if (np.unique(target_list).size < 2): #if device count <2
		makeclf = False
		print("At least 2 device types needed.")
	for element in set(target):
		temp = target_list.count(element)
		print(element, "has", temp, "inputs")
		if (temp < minimum):
			print("needs", minimum-temp, "more inputs")
			makeclf = False
	return makeclf # if True make classifier

def record(spectrum):
	#Why is data analysis and processing happening in the record() function?
	#Why is this extra data analysis happening at all? If this should remain,
	#it needs to be put elsewhere.
	for i in range(0, spectrum.size):
		spectrum[i] /= mean

	device = sys.argv[len(sys.argv)-2]

	#scikit nearest neighbors requires two sets of inputs
	#a set of signatures that correspond to a set of classifications
	#variables named data and target here
	data = np.array([[]])
	target = np.array([])
	#pickle stores a dictionary of data, target, and the classifier
	#if pickle file exists, open it
	if os.path.isfile(picklename):                                               
		f = open("clf.p", "r+")
		combined = pickle.load(f)
		data = combined['data']
		target = combined['target']
		f.close()
		data = np.append(data, [spectrum], axis=0)
	else:
		data = np.append(data, [spectrum], axis=1)
	target = np.append(target, [device], axis=0)

	makeclf = count_inputs(target) #checks if enough data to make target now
	clf = None #classifier
	if (makeclf == True):
		print("make clf")
		clf = neighbors.NearestCentroid()
#	clf = neighbors.NearestCentroid() if (makeclf == True) else None
	if (clf != None):
		print("make fit")
		clf.fit(data, target)
	#dictionary so just one object would be pickled
	combined = {'data':data, 'target':target, 'clf':clf}
	f = open("clf.p", "w+")
	pickle.dump(combined, f) #stores pickle
	f.close()


def classify(spectrum):
	variation_coefficient = standard_deviation
	#for i in range(0, spectrum.size):
	#	spectrum[i] /= mean
	#already normalized, no need to divide by mean again..
	clf = None #classifier
	if os.path.isfile(picklename): #reads in classifier, if it exists                                               
		f = open("clf.p", "r+")
		combined = pickle.load(f)
		clf = combined['clf']
		f.close()
	else:
		print("there is no classifier!")

	if (clf):
		print("recorded from", clf.predict(spectrum)[0])
		# .predict returns a one-dimensional array, so take index 0
	else:
		print("More input needed to create a classifier:")
		count_inputs(target) #prints out what is needed to make a classifier

#Execution begins here
if __name__ == "__main__":
	classification_data = np.array([])
	classification_target = np.array([])
	Blockwidth = 200
	Currents = []
	filename_arg_index = len(sys.argv) - 1
	if (os.path.isfile(sys.argv[filename_arg_index]) == False):
			print_help()
			exit(0)
	Options = init()
	Currents = import_and_trim(Currents)
	Blocklist = produce_blocklist()
	Spectrum = produce_mean_normalized_power_spectrum(Blocklist)

	#mean and std are used by both display() and classify()
	#only calculate once.
	mean = np.mean(Spectrum)
	standard_deviation = np.std(Spectrum)

	picklename = "clf.p"

	#This should be done first
	if 'h' in Options:
		print_help()
	if 'c' in Options:
		if len(sys.argv) < 3:
			print_help()
		else:
			classify(Spectrum)
	if 'p' in Options:
		print(Spectrum)
	if 'w' in Options:
		write_output()
	if 'v' in Options or 'V' in Options:
		display(Spectrum)
	if 'r' in Options:
		if len(sys.argv) < 4:
			print_help()
		else:
			record(Spectrum)
