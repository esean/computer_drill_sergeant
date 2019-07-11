#!/bin/bash
INF="${1:-pushups}"

###########
MIN=0.2		# sec
MAX=1.0		# sec
#MIN=0.35		# sec
#MAX=1.1		# sec
#dur=3		# init, sec
dur=8		# init, sec
MULT=1.25	# keeps multiplying...
###########

#------------------
export PATH=$PATH:$PWD
die() { echo "ERROR:$0:$@ !"; exit 1; }
is_linux=0
case X"$OSTYPE" in
    X*linux*)  is_linux=1;;
esac

if [ $is_linux -eq 0 ]; then
    #VOICEs="Sara"
    #VOICEs="Sara Nora Veena"
    VOICEs="Juan Kanya Fiona"
else
    #VOICEs="cantonese aragonese georgian"
    VOICEs="english malay english-north" #bosnian czech danish"
    #VOICEs="afrikaans aragonese bulgarian bosnian catalan czech welsh danish german greek default english en-scottish english-north english_rp english_wmids english-us en-westindies esperanto spanish spanish-latin-am estonian persian persian-pinglish finnish french-Belgium french irish-gaeilge greek-ancient hindi croatian hungarian armenian armenian-west indonesian icelandic italian lojban georgian kannada kurdish latin lingua_franca_nova lithuanian latvian macedonian malayalam malay nepali dutch norwegian punjabi polish brazil portugal romanian russian slovak albanian serbian swedish swahili-test tamil turkish vietnam vietnam_hue vietnam_sgn Mandarin cantonese"
fi

#----------
_say() {
    opt=''
    case X"$1" in
        X-v) shift; voice="$1"; shift; opt="-v $voice";; 
    esac
    if [ $is_linux -eq 1 ]; then
        echo "$@" | espeak $opt
    else
        say $opt "$@"
    fi
}
vlog() { echo "[$voice]:$@"; }
#----------
# 1 = voice
# 2 = file
# 3 = min
# 4 = max
# 5 = duration
# always ends on out/down
ALL=/tmp/sss.all
run_set() {
    voice="$1"
    U=/tmp/$voice

	# run file and say for time
	# log to same logfile since start so can count cycles
	repetitionSayer.py -v $1 -f $2 -a $3 -s $4 -t $5 | tee -a $U | tee -a $ALL | grep '^Total time: '

	# end of out/down, say the 'down' statement
	case "`tail -n 2 $U`" in
		*\ up\ *)   last_action_term='down'
            ;;
		*\ down\ *)   last_action_term='up'
            ;;
        *\ in\ *)   last_action_term='out'
            ;;
        *\ out\ *)   last_action_term='in'
            ;;
        *)  die "Unknown run_set():`tail -n 2 $U`"
            ;;
    esac

	# count cycles from logfile
	echo -n " +> counted ${last_action_term}'s: "; cat $ALL | grep $last_action_term | wc -l 	# same reason here
    latest_cnt=`cat $ALL | grep $last_action_term | wc -l | awk '{print $1}'`

    # end cycle in a defined state
	case "`tail -n 2 $U`" in
        *\ up\ *)
            sleep $3
            _say -v $1 "$last_action_term"
            sleep $3
            ;;
        *\ in\ *)
            sleep $3
            _say -v $1 "$last_action_term"
            sleep $3
            ;;
    esac

    _say -v $1 "$latest_cnt sets" &
    sleep 0.1

    # TASK DONE: update 'done' file
    echo "($voice) RUN_SET() TASK DONE" | tee /tmp/done_file-$voice
}
#----------
# 1 = voice
# 2 = sleep time before countdown
# 3 = phrase to say
rest_set() {
    v="$1"; shift
	show_running_time $v
	slp=$1; shift
    _say -v $v "$@"
    sleep $slp
    _say -v $v "3"
    sleep 0.5
    _say -v $v "2"
    sleep 0.5
    _say -v $v "1" &
    sleep 0.5

    # update 'done' file
    echo "($v) REST_SET() TASK DONE" | tee /tmp/done_file-$v
}
#----------
# $1 = voice
show_running_time() {
	now_tm=`date +%s`
	del_tm="`echo "$now_tm-$start_tm" | bc -l`"
	echo "Running time: $del_tm sec"
    _say -v $1 "in $del_tm seconds"
}
#----------
mk_float () { awk '{printf("%0.25f\n",$1)}'; }

[ ! -f $INF ] && die "Cannot find input file:$INF"

_say "starting"
for voice in $VOICEs; do
    _say -v $voice "hi" &
    sleep 0.1
done
start_tm=`date +%s`
sleep 2

# $@ = voices
wait_for_all_voices_to_complete() {
	for voice in $@; do
        while [ ! -f /tmp/done_file-${voice} ]; do
            echo -n "($voice) "
            sleep 0.1
        done
        echo "DONE:$voice"
    done
}

# remove any previous log files
rm -f $ALL
for voice in $VOICEs; do
    #U=/tmp/$voice
    rm -f /tmp/$voice # $U
done

while :; do
	
	for voice in $VOICEs; do
    #    rm -f /tmp/done_file-${voice}
		run_set $voice $INF $MIN $MAX $dur
	done
    #wait_for_all_voices_to_complete $VOICEs

	dur="`echo "$dur*$MULT" | bc -l | mk_float`"
	MIN="`echo "$MIN*$MULT" | bc -l | mk_float`"
	MAX="`echo "$MAX*$MULT" | bc -l | mk_float`"

	for voice in $VOICEs; do
        rm -f /tmp/done_file-${voice}
	    rest_set $voice 2 "now rest" &
    done
    wait_for_all_voices_to_complete $VOICEs

done

