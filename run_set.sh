#!/bin/bash
INF="${1:-pushups}"
#VOICEs="Sara Nora Veena"
VOICEs="Juan Kanya Fiona"
###########

MIN=0.2		# sec
MAX=1.0		# sec
#MIN=0.35		# sec
#MAX=1.1		# sec
dur=8		# init, sec
MULT=1.25	# keeps multiplying...

###########


export PATH=$PATH:$PWD
#----------
# 1 = voice
# 2 = file
# 3 = min
# 4 = max
# 5 = duration
U=`mktemp /tmp/tmp.XXXXXXXXXX`
# always ends on out/down
run_set() {
	# run file and say for time
	# log to same logfile since start so can count cycles
	repetitionSayer.py -v $1 -f $2 -a $3 -s $4 -t $5 | tee -a $U | grep '^Total time: '

	# end of out/down, say the 'down' statement
	last_ln="`tail -n 2 $U | head -n 1`"	# 2nd to last line, last line is runtime it took 
	case "$last_ln" in
		*\ up\ *) sleep $3; say -v $1 "down" | tee -a $U; sleep $3
			;;
	esac

	# count cycles from logfile
	echo -n " +> counted UP's: "; cat $U | grep down | wc -l 	# same reason here
}
#----------
# 1 = sleep time before countdown
# 2 = phrase to say
rest_set() {
	show_running_time
	slp=$1; shift
        say "$@"
        sleep $slp
        say "3"
        sleep 0.5
        say "2"
        sleep 0.5
        say "1"
        sleep 0.5
}
#----------
show_running_time() {
	now_tm=`date +%s`
	del_tm="`echo "$now_tm-$start_tm" | bc -l`"
	echo "Running time: $del_tm sec"
}
#----------
mk_float () { awk '{printf("%0.25f\n",$1)}'; }

say "starting"
start_tm=`date +%s`
sleep 3

while :; do
	
	for voice in $VOICEs; do
		run_set $voice $INF $MIN $MAX $dur
		sleep 0.1	# ctrl-c
	done

	dur="`echo "$dur*$MULT" | bc -l | mk_float`"
	MIN="`echo "$MIN*$MULT" | bc -l | mk_float`"
	MAX="`echo "$MAX*$MULT" | bc -l | mk_float`"

	rest_set 2 "now rest"
done

