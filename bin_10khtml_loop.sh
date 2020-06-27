#!/bin/bash

for i in $(seq 100 100 1600 $END); do
	let ENDROW=i+100;
	( python main_10khtml.py --starting_row $i --ending_row $ENDROW )
done
