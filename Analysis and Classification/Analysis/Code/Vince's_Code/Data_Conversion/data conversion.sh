#!/bin/bash

##
# To-do:
# * Make this into a function and recurse through subdirectores
##

filename_seed=_amps_time.csv 
#descent_counter=0
for i in $(ls); do
	#If we see a raw file...
	if [[ `echo $i | egrep 'raw.csv'` != "" ]]; then 

		#Create the new file name.
		trimmed_original_filename=`echo $i | sed 's/\([^.]\)[.][c][s][v]$/\1/'`
		filename="$trimmed_original_filename$filename_seed"

		#Don't convert if it already exists
		if [ ! -f $filename ]; then
			echo "Trimming $i..."
			cat $i | egrep '^70|^66|^74|^62|^78|^58|^50|^14|^54' | sed 's/^[0-9][0-9][,]\([-0-9][0-9]*[\.]*[0-9]*[,][0-9][0-9]*\)[,][0-9][0-9]*/\1/' > $filename
		else
			echo "Skipping $i..."
		fi
	fi;
done

echo "Done"
