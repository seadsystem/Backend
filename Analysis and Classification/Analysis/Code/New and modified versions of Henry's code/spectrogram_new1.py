#!/usr/bin/python
# ==========================================================================
# File: spectrogram.py
# Description: Takes in alternating current data from plug,
# .csv export
#              usage: spectrogram.py [folder path directory][sensor ID's]
# Created by Henry Crute
# 9/16/2014
# Modified by Diem Chau
# 11/10/14
# ==========================================================================

import sys, os
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from pylab import *

#from openpyxl import load_workbook
#creates folder if it doesn't exist in the directory
def ensure_dir(directory):
   if not os.path.exists(directory):
      os.makedirs(directory)

#multiplies data array by some offset that corresponds to the bins from shemp adc
def correct_ac_data(ac):
   #print ac
   ac[:] = [x * 27.306 for x in ac]
   #print ac

#gets data from file
def get_data(filename, wattage, temperature, ac, voltage):
    #filename = load_workbook(filename, use_iterators = True)
   for line in filename:
      line_id = line[:2]
      if ac_id in line_id:
         ac.append(float(line.split(delimiter)[1]))
      elif voltage_id in line_id:
         voltage.append(float(line.split(delimiter)[1]))
      elif wattage_id in line_id:
         wattage.append(float(line.split(delimiter)[1]))
      elif temperature_id in line_id:
         temperature.append(float(line.split(delimiter)[1]))
   correct_ac_data(ac)

def visualize_data(wattage, temperature, ac, voltage, filename):
   ensure_dir(output_dir + filename)
   plt.figure()
   plt.title('Power from ' + filename)
   plt.xlabel('Seconds')
   plt.ylabel('Watts')
   x = np.arange(0, len(wattage) * 5, 5)
   plt.plot(x, wattage, 'r',
            x, wattage, 'ro')
   savefig(output_dir + filename + '/' + filename + '_watt' + '.png')
   plt.figure()
   plt.title('Temperature from ' + filename)
   plt.xlabel('Seconds')
   plt.ylabel('Celcius')
   x = np.arange(0, len(temperature) * 5, 5)
   plt.plot(x, temperature, 'k',
            x, temperature, 'ko')
   savefig(output_dir + filename + '/' + filename + '_temp' + '.png')
   plt.figure()
   plt.subplot(211)
   plt.title('AC and Voltage from ' + filename)
   plt.xlabel('Seconds')
   plt.ylabel('Milliamps')
   x = np.linspace(0.0, len(ac) / 2400.0, len(ac))
   plt.plot(x, ac, 'b')
   plt.subplot(212)
   plt.xlabel('Seconds')
   plt.ylabel('Voltage')
   x = np.linspace(0.0, len(voltage) / 2400.0, len(voltage))
   plt.plot(x, voltage, 'g')
   savefig(output_dir + filename + '/' + filename + '_ac_voltage' + '.png')

def visualize_spec(signal, signal_type, filename):
   ensure_dir(output_dir + filename)
   fig = plt.figure(figsize=(8, 10))
   dt = 1.0/2400.0 #sampling rate
   t = np.linspace(0.0, len(signal) / 2400.0, len(signal)) #time bins
   NFFT = 2048 #length of fft segments
   window_len = NFFT/2
   n_overlap=np.fix(window_len/2)
   p_to = 8 * window_len
   Fs = int(1.0/dt)
   #original signal
   ax1 = plt.subplot(211)
   plt.title('Signal, and Power Spectral Density of a ' + filename)
   plt.xlabel('Seconds')
   if signal_type == 'Amperage':
      plt.ylabel('Milliamps')
   elif signal_type == 'Voltage':
      plt.ylabel('Volts')
   plt.plot(t, signal)
   #spectrogram PSD
   ax2 = plt.subplot(212, sharex=ax1)
   plt.ylabel('Hertz')
   plt.yticks(np.arange(0, Fs/2, 120))
   plt.xlabel('Seconds')
   Pxx, freqs, bins, im = specgram(signal, NFFT=NFFT, Fs=Fs,
                                   detrend=mlab.detrend_linear,
                                   noverlap=n_overlap, cmap=None,
                                   pad_to = p_to, scale_by_freq=True,
                                   mode='default')
   ax2.set_autoscaley_on(False)

   #spectrogram key
   #cb = plt.colorbar(im, ticks=np.arange(-1000,1000,10), orientation='horizontal',
    #                 spacing='proportional')
   cb = plt.colorbar(im, ticks=np.arange(-1000,1000,10), orientation='horizontal',spacing='uniform')
   cb.set_label('Power (dB)')
   ax3 = ax2.twinx()
   plt.ylabel('Harmonic Number')
   plt.yticks(np.arange(0, 21, 1))

   savefig(output_dir + filename + '/' + filename + '_' + signal_type + '_psd.png')

   #spectrogram angle
   fig = plt.figure(figsize=(8, 4.5))
   ax1 = plt.subplot(111)
   plt.title(signal_type + ' Angle Spectrogram of a ' + filename)
   plt.ylabel('Hertz')
   plt.yticks(np.arange(0, Fs/2, 120))
   plt.xlabel('Seconds')
   Pxx, freqs, bins, im = specgram(signal, NFFT=NFFT, Fs=Fs,
                                   detrend=mlab.detrend_linear,
                                   noverlap=n_overlap, cmap=None,
                                   pad_to = p_to, scale_by_freq=True,
                                   mode='angle')

   #spectrogram key
   cb = plt.colorbar(im, ticks=[-pi, -pi/2, 0, pi/2, pi], orientation='horizontal',
                     spacing='proportional')
   cb.set_label('Angle (radians)')
   ax2 = ax1.twinx()
   plt.ylabel('Harmonic Number')
   plt.yticks(np.arange(0, 21, 1))

   savefig(output_dir + filename + '/' + filename + '_' + signal_type + '_angle.png')
   #spectrogram phase
   fig = plt.figure(figsize=(8, 4.5))
   ax1 = plt.subplot(111)
   plt.title(signal_type + ' Phase Spectrogram of a ' + filename)
   plt.ylabel('Hertz')
   plt.yticks(np.arange(0, Fs/2, 120))
   plt.xlabel('Seconds')
   Pxx, freqs, bins, im = specgram(signal, NFFT=NFFT, Fs=Fs,
                                   detrend=mlab.detrend_linear,
                                   noverlap=n_overlap, cmap=None,
                                   pad_to = p_to, scale_by_freq=True,
                                   mode='phase')

   #spectrogram key
   cb = plt.colorbar(im, ticks=np.arange(-10000,1000,200), orientation='horizontal',
                     spacing='proportional')
   cb.set_label('Phase (radians)')
   ax2 = ax1.twinx()
   plt.ylabel('Harmonic Number')
   plt.yticks(np.arange(0, 21, 1))

   savefig(output_dir + filename + '/' + filename + '_' + signal_type + '_phase.png')


def process_data(file_directory):
   plugread = open(file_directory, 'r')
   filename = os.path.basename(file_directory)
   print filename
   wattage = []
   temperature = []
   ac = []
   voltage = []
   #populates arrays from mysql 'into outfile' command
   get_data(plugread, wattage, temperature, ac, voltage)
   plugread.close()

   visualize_data(wattage, temperature, ac, voltage, filename)
   #visualize_spec(voltage, 'Voltage', filename)
   visualize_spec(ac, 'Amperage', filename)
   plt.show()


#START OF PROGRAM
if len(sys.argv) < 6:
   print "Use .csv file only\n"
   print "usage: " + sys.argv[0] + " [input folder path dir] [output folder path] [ac_id] [wattage_id] [temperature_id]"
   exit(1)

#opens specified directory to read from
path = sys.argv[1]

#opens output directory to output files
output_dir = sys.argv[2]

#defined sensor ID's
wattage_id = sys.argv[4]
temperature_id = sys.argv[5]
ac_id = sys.argv[3]
voltage_id = '13'

#delimiter for Microsoft Excel(.csv) file
delimiter = ','

for root, dirs, filenames in os.walk(path):
   for f in filenames:
      absolute_path = path + f
      process_data(absolute_path)

