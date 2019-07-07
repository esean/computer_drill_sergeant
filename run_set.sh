#!/bin/bash
INF="${1:-pushups}"
#VOICEs="Sara Nora Veena"
#VOICEs="english-north"
#VOICEs="Juan Kanya Fiona"
#VOICEs="cantonese aragonese georgian"
VOICEs="bosnian czech danish"
#VOICEs="afrikaans aragonese bulgarian bosnian catalan czech welsh danish german greek default english en-scottish english-north english_rp english_wmids english-us en-westindies esperanto spanish spanish-latin-am estonian persian persian-pinglish finnish french-Belgium french irish-gaeilge greek-ancient hindi croatian hungarian armenian armenian-west indonesian icelandic italian lojban georgian kannada kurdish latin lingua_franca_nova lithuanian latvian macedonian malayalam malay nepali dutch norwegian punjabi polish brazil portugal romanian russian slovak albanian serbian swedish swahili-test tamil turkish vietnam vietnam_hue vietnam_sgn Mandarin cantonese"
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
_say() {
    case X"$1" in
        X-v) shift; voice="$1"; shift; echo "$@" | espeak -v $voice;;
        *) echo "$@" | espeak;;
    esac
}

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
	echo "repetitionSayer.py -v $1 -f $2 -a $3 -s $4 -t $5 | tee -a $U | grep '^Total time: '"
	repetitionSayer.py -v $1 -f $2 -a $3 -s $4 -t $5 | tee -a $U | grep '^Total time: '

	# end of out/down, say the 'down' statement
	last_ln="`tail -n 2 $U | head -n 1`"	# 2nd to last line, last line is runtime it took 
	case "$last_ln" in
		*\ up\ *) sleep $3; _say -v $1 "down" | tee -a $U; sleep $3;;
		*\ in\ *) sleep $3; _say -v $1 "out" | tee -a $U; sleep $3;;
	esac

	# count cycles from logfile
	echo -n " +> counted UP's: "; cat $U | grep out | wc -l 	# same reason here
	#echo -n " +> counted UP's: "; cat $U | grep down | wc -l 	# same reason here
}
#----------
# 1 = sleep time before countdown
# 2 = phrase to say
rest_set() {
	show_running_time
	slp=$1; shift
    _say "$@"
    sleep $slp
    _say "3"
    sleep 0.5
    _say "2"
    sleep 0.5
    _say "1"
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

_say "starting"
for voice in $VOICEs; do
    _say -v $voice "hi"
done
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

