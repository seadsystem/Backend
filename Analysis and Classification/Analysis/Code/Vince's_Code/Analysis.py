#/usr/bin/python

##
# Analysis.py
# Author: Vincent Steffens
# Email:  vsteffen@ucsc.edu
# Date:   7 November 2014
#
# This script is intended to perform exploratory analysis on amperage 
# data provided by the SEAD plug. This script takes as input one 
# filename in the current directory.
#
# =================================================================== #
# Outline                                                             #
# =================================================================== # 
#
# Section I: Read and Prepare the Data
#
# 1. Open the file for reading
# 2. Read the lines of the file into two arrays, one for amperage 
#    data and one for time data.
# 3. Scale the amperage data to produce an array of milliamp values. 
# 4. Subtract the earliest time from each timestamp to produce a 
#    timescale somewhat more intellectually manageable. 
# 5. Use fft to produce a numerical spectrogram; a 2-D array in which 
#	  one dimension is time and the other, frequency. The elements are 
#    intensity values.  
#
# Section II: Perform Spectral Analysis
# 
# 	  We're not just looking to take the FT. We need a power spectrum, 
#    which is defined as
#       power_spectrum(f(t)) = |FT(f(t)|^2
# 
# Section II: Extract Statistical Information
#
# 1. For each frequency bin, sum find the mean and standard deviation. 
# 2. Produce a "mean power spectrum", and visualize this.
# -Note: This is a good stopping point for this week
#
# Section III: Produce a Signature
# 1. Pick peaks, find mean and standard deviation for frequency 
#    domain.
# 2. Construct an ADT object that holds these values.
#
#
# =================================================================== # 
# Options                                                             #
# An option must be given as the first argument.                      #
# =================================================================== # 
# 
# -d: Debug mode
# -f: Fragmented data mode
#
# =================================================================== # 
# Return Values                                                       # 
# =================================================================== #
#
# -1: Too few arguments
# -2: Too many arguments
# -3: Possible misplaced option
# -4: File does not exist!
#
# =================================================================== # 
# Questions                                                           # 
# =================================================================== #
#
# Questions relevant to the data
# 1. How accurate is the sampling rate? What is its deviation?
# 2. What's a good minimum number of bins for the FFT / power 
#    spectrum?
#
# =================================================================== # 
# TO DO                                                               # 
# =================================================================== #
#
# 1. Take power spectrum instead of FFT
# 2. Specify delta_t to spectral analysis function
# 3. Normalize power spectra by their integral from 0 to freq_max
# 4. Find a way to get the input from the database (talk with Ian, 
#    Raymond and Q)
# 5. Produce the mean power spectrum and standard deviation /for 
#    each array index/. It will probably become necessary to use a 
#    feature extractor, and because we're analyzing power usage data 
#    this should probably be its input.
# 6. Find a decent way to ouptut signatures so that they can be read
#    in and used.  
##

#For numerical analysis
import numpy 

#For visualization
import matplotlib.pyplot as pyp

#For manipulating command-line arguments
import sys

#For handling files
import os.path as op

#For using regular expressions
import re

#For saving files
import os

#Check for proper number of arguments, die if necessary
#max_args should be the sum of: 1 for program name, the number of 
#options, 1 for the input file name
max_args = 4
if len(sys.argv) < 2:
	print "Usage Message A: <program name> [option] <input file name>"
	sys.exit(-1)
if len(sys.argv) > max_args:
	print "Usage Message B: <program name> [option] <input file name>"
	sys.exit(-2)  

#This is done in a way that works, but is incorrect and should be fixed
#Check for options, set flags, die if necessary
debug = 0
fragmented_data = 0
flags_set = 0
flag_regex = re.compile('[-]([d]*)([f]*)')
for i in xrange(1, len(sys.argv) - 1):
	option = flag_regex.match(sys.argv[i])
	if option == None:
		print "Usage Message C: <program name> [option] <input file name>"
		sys.exit(-3)
	if option.group(1) == 'd':
		debug = 1
		flags_set = flags_set + 1
	if option.group(2) == 'f':
		fragmented_data = 1
		flags_set = flags_set + 1 

#Loop through the arguments (for my own benefit)
if debug == 1:
	for i in xrange(0, len(sys.argv)):
		print "Argument ", i, ": ", sys.argv[i]

#Try to open source file for reading
filename = sys.argv[len(sys.argv) - 1]
if op.isfile(filename):
	with open(filename) as f:
		content = [x.strip('\n') for x in f.readlines()]
else: 
	print "Analysis: file does not exist: ", filename
	sys.exit(-4)


#Parse the strings and put each datum into its own list
Currents = []
Times = []
regexpr = re.compile('\A([-]*[0-9][0-9]*)[,]([0-9][0-9]*)')
for i in xrange(0, len(content)):
	result = regexpr.match(content[i])
	Currents.append(result.group(1))
	Times.append(result.group(2))

#Convert time since Unix epoch to intervals in microseconds
#Convert currents to milliamps
Times = [ int(x) - int(Times[0]) for x in Times ]
Currents = [ 27*float(x)/1000 for x in Currents ]

#For looking at the data in column format
if debug == 1:
	print "Printing Differences"
	d_current = []
	d_time = []

	#take first-order finite difference
	for i in xrange(0, len(Currents) - 1):
		d_time.append(Times[i + 1] - Times[i])
		d_current.append(Currents[i + 1] - Currents[i])

	#Print nicely
	skipped_time = 0
	spent_time = 0
	for i in xrange(0, len(d_current)):
		#This tab is just for ease-of-reading
		output_string = "Item " + str(i) + ":\t" + str(d_time[i]) + "\t"

		if d_time[i] > 417:
			skipped_time += d_time[i]
		elif d_time[i] <= 417:
			spent_time += d_time[i]

		if d_current[i] >= 0:
			output_string += " "
		
		output_string += str(d_current[i])
		print output_string

	#Convert to seconds
	spent_time *= 10**-6
	skipped_time *= 10**-6
	total_time = skipped_time + spent_time
	proportion = float(skipped_time)/total_time
	print "Skipped time:\t\t\t", skipped_time
	print "Spent time:\t\t\t", spent_time
	print "Elapsed time:\t\t\t", total_time
	print "Proportion of skipped to total:\t", proportion
	print "Time in seconds."

	the_fft = numpy.fft.rfft(Currents)
	the_real_fft = numpy.absolute(the_fft)
	pyp.plot(the_real_fft)
	pyp.savefig(filename + ".png", bbox_inches='tight')
	#pyp.show()

#Create a list of lists of 200-point contiguous chunks
if fragmented_data == 1:
	chunklist = []
	
	data_length = len(Currents) #or Times, just to de-specify
	i = 0
	while i < data_length:
		chunk = []

		j = i
		while j < data_length: 
			if j + 1 < data_length and Times[j + 1] - Times[j] < 418:
				chunk.append(Currents[j])
			else: 
				break
			j += 1
		chunklist.append(chunk)
		i = j + 1

	#produce a mean frequency spectrum
	#convert to numpy arrays, scale, sum
	from operator import add
	scale_factor = float(1)/len(chunklist)

	the_fft = numpy.fft.rfft(chunklist[0])                            
	the_real_fft = numpy.absolute(the_fft)                            
	mean_distribution = scale_factor * the_real_fft
	for i in xrange(1, len(chunklist)):
		the_fft = numpy.fft.rfft(chunklist[i])                             
		the_real_fft = numpy.absolute(the_fft) 
		the_scaled_fft = scale_factor * the_real_fft
		mean_distribution = map(add, mean_distribution, the_scaled_fft)	

#bleeding edge begins here
"""
	#display
	for i in xrange(0, len(chunklist)):
		print chunklist[i]
		print "length: %d, i: %d" % (len(chunklist[i]), i)
		the_fft = numpy.fft.rfft(chunklist[i])                                   
		the_real_fft = numpy.absolute(the_fft)                               
		pyp.plot(the_real_fft)                                               
		pyp.savefig(filename + str(i) + ".png", bbox_inches='tight')                  
		#pyp.show()
"""


mean_value = numpy.mean(mean_distribution)
std_dist = numpy.std(mean_distribution)

template = numpy.ones(len(mean_distribution))

pyp.plot(mean_distribution)
for i in xrange(0, 5):
	pyp.plot(template * (mean_value + i * std_dist))
pyp.xlabel('Frequency')
pyp.ylabel('Intensity')
pyp.title('Mean Frequency Distribution')
#pyp.show()
pyp.savefig(filename + "_mean.png")

"""
for i in xrange(0, len(the_real_fft)):
	if the_real_fft[i] < 0:
		print [i]
#for i in xrange(0, len(the_real_fft)):                             
#	if mean_distribution[i] >= 0:                                         
#		print mean_distribution[i] 
mean_value = numpy.mean(the_real_fft)
print "mean value:", mean_value
"""
