#!/bin/bash

for i in $(seq 100 100 900 $END); do
	let ENDROW=i+100;
	( //anaconda3/bin/python main_10khtml.py --starting_row $i --ending_row $ENDROW --proxy & )
done