#Title: Time Analyzer
#Author: Vincent Steffens
#Date: 8 November 2014
#Email: vsteffen@ucsc.edu
#
# This file is a wrapper script for Analysis.py and is intended to be 
# used to output time usage data for amperage-and-time-only data files 
# containing data from the SEAD plugs.

index=0
echo "" > results.txt
echo "Analyzing amp_data_iof/ ..."; 
for i in $(ls amp_data_iof); do
	((++index))
	echo $index
	echo "Analyzing $i"
   echo "Analyzing $index" >> results.txt
   python Time_Analysis.py amp_data_iof/$i >> results.txt
   echo >> results.txt
done
