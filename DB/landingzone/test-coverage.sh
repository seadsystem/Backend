#!/bin/bash
# Script from https://github.com/gopns/gopns

echo "mode: set" > acc.out
for Dir in $(find $1/* -maxdepth 10 -type d ); 
do
	if ls $Dir/*.go &> /dev/null;
	then
		returnval=`go test -coverprofile=profile.out $Dir`
		echo ${returnval}
		if [[ ${returnval} != *FAIL* ]]
		then
    		if [ -f profile.out ]
    		then
        		cat profile.out | grep -v "mode: set" >> acc.out 
    		fi
    	else
    		exit 1
    	fi	
    fi
done

if [ -n "$COVERALLS" ]
then
	echo "COVERALLS: $COVERALLS"
	$GOPATH/bin/goveralls -coverprofile=acc.out -service=travis-ci -repotoken=$COVERALLS
fi

rm -rf ./profile.out
rm -rf ./acc.out
