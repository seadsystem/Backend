#!/bin/bash
for i in $(ls *.csv); do 
	if [[ `echo $i` != "Analysis.py" ]]; then 
		if [[ `echo $i` != "demo.sh" ]]; then
 			python Analysis.py -c $i; 
		fi;
	fi 
done
