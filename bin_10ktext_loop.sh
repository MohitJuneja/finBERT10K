#!/bin/bash

for i in $(seq 600 100 900 $END); do
	let ENDROW=i+100;
	# echo $i;
	# echo $ENDROW;
	( //anaconda3/bin/python main_10ktext.py --starting_row $i --ending_row $ENDROW --proxy & )
done