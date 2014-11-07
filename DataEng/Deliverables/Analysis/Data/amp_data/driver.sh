#!/bin/bash

append=_amp_data;                                                 
for i in $(ls); do 
	if [ -d $i ]; then 
		#go into the directory, bring the converter, run it, go back out
      #and bring the converter with
		mv data\ conversion.sh $i;
		cd $i;
      ./data\ conversion.sh;                                            
      mv data\ conversion.sh ..;                                        
      cd ..; 

		#make a directory for the amp data and put it there
		filename=$i$append; 
		mkdir $filename; 
		mv $i/*amps* $filename; 
		mv $i/log.txt $filename; 
fi; 
done
