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
# 2. What's a good number of bins for the FFT?
#
# =================================================================== # 
# TO DO                                                               # 
# =================================================================== #
#
# 1. Enable the program to handle any number of arguments
##

#For numerical analysis
import numpy as np

#For visualization
import matplotlib.pyplot as pyp

#For manipulating command-line arguments
import sys

#For handling files
import os.path as op

#For using regular expressions
import re

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

#Check for options, set flags, die if necessary
debug = 0
fragmented_data = 0
flags_set = 0
flag_regex = re.compile('([-][df])')
for i in xrange(1, len(sys.argv) - 1):
	option = flag_regex.match(sys.argv[i])
	if option == None:
		print "Usage Message C: <program name> [option] <input file name>"
		sys.exit(-3)
	if option.group() == '-d':
		debug = 1
		flags_set = flags_set + 1
	elif option.group() == '-f':
		fragmented_data = 1
		flags_set = flags_set + 1 

#Loop through the arguments (for my own benefit)
if debug == 1:
	for i in xrange(0, len(sys.argv)):
		print "Argument ", i, ": ", sys.argv[i]

#Try to open source file for reading
filename = sys.argv[1 + flags_set]
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

#Convert time since Unix epoch to intervals in milliseconds
#Convert currents to milliamps
first = Times[0]
Times = [ int(x) - int(Times[0]) for x in Times ]
Currents = [ 27*float(x)/1000 for x in Currents ]

#For looking at the data in columns
if debug == 1:
	print "debug marker"
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
		output_string = "Item "
		if d_time[i] > 417:
			output_string += str(i) + ":\t" + str(d_time[i]) 
			skipped_time += d_time[i]
		if d_time[i] <= 417:
			spent_time += d_time[i]
#		output_string += str(i) + ":\t" + str(d_time[i]) + "\t"
#		if Currents[i] >= 0:
#			output_string += " "
		
#		output_string += str(Currents[i])

			print output_string
	print "Skipped time:", skipped_time
	print "Spent time:", spent_time
	#plot currents
	pyp.plot(d_current)
	pyp.ylabel("di")
	pyp.xlabel("dt")
#	pyp.show()


#Find spent time, skipped time, and proportion. Print each.
d_time = []                                                          

#take first-order finite difference                                  
for i in xrange(0, len(Times) - 1):                               
	d_time.append(Times[i + 1] - Times[i]) 


#calculate
skipped_time = spent_time = 0.0

for i in xrange(0, len(d_time)):
   output_string = "Item "
   if d_time[i] > 417:
      skipped_time += d_time[i]
   if d_time[i] <= 417:
      spent_time += d_time[i]
spent_time *= 10**-6
skipped_time *= 10**-6 
total_time = skipped_time + spent_time
proportion_skipped_to_total = float(skipped_time)/total_time
print "Skipped time in seconds:", skipped_time
print "Spent time:", spent_time
print "Elapsed time:", total_time
print "Proportion of skipped to total:", proportion_skipped_to_total


