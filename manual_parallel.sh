#!/bin/bash

for i in $(seq 200 100 1700 $END); do 
	let ENDROW=i+100;
	//anaconda3/bin/python manual_parse_script.py --starting_row $i --ending_row $ENDROW &
done