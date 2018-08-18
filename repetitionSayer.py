#!/usr/bin/env python2.7
import sys
import re
import os
import getopt as go
import time
import glob
from datetime import datetime
import json
#import calendar as cal
import python_helpers as ph
import random

#----------------------------------
def usage():
    print
    print "%s -v [voice] -f [program file to run] {-t [run X seconds]}" % os.path.basename(sys.argv[0])
    print
    print "Runs [program file] line-by-line and either sleeps, or says something"
    print
    print "   # COMMENTS ignored"
    print "   0,hi1"
    print "   rand,hi2"
    print "   randsmall,hi3"
    print 
    print " will repeat those forever, or some [run X seconds] amount of seconds"
    print
    print "opt.param [-a,-s] set [rand_start,stop]"
    print "Or, use '-l' param to list available voices"
    print
    print "Example"
    print "     $ ./repetitionSayer.py -f file -a 2 -s 8 -t 60"
    print

#----------------------------------
if __name__ == '__main__':

    voice = "Yuna" #"Kyoko"
    filenm = str()
    run_sec = 0
    rand_start = 3.0
    rand_stop = 20.0
    
    try:
        opts, args = go.getopt(sys.argv[1:], "hv:f:t:a:s:l", ["help", "voice=", "program_script_filename=", "run_sec=", "rand-time-start=", "rand-time-stop=", "list-voices" ])
    except go.GetoptError as message:
        sys.exit("Error:%s" % message)
    for option, argument in opts:
        if option in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif option in ('-v', '--voice'):
            voice = str(argument)
        elif option in ('-f', '--program_script_filename'):
            filenm = str(argument)
        elif option in ('-t', '--run_sec'):
            run_sec = float(argument)
        elif option in ('-a', '--rand-time-start'):
            rand_start = float(argument)
        elif option in ('-s', '--rand-time-stop'):
            rand_stop = float(argument)
        elif option in ('-l', '--list-voices'):
            cmd = "say -v ?"
            (ret,txt) = ph.run_subprocess(cmd)
            print txt
            sys.exit(0)
    if not voice or not filenm:
        usage()
        ph.die("Incorrect params")

    starttime = datetime.now()
    while True:
        
        # read one file
        with open(filenm, 'r') as in_file:
            for ln in in_file:
                ln = ln.rstrip()
                if ln.startswith('#'):
                    continue
                
                row = re.split(',',ln,2)
                if 'randsmall' in str(row[0]):
                    sleep_time = random.uniform(0, rand_start)
                elif 'rand' in str(row[0]):
                    sleep_time = random.uniform(rand_start, rand_stop)
                else:
                    sleep_time = float(row[0])
                saytxt = str(row[1])

                time.sleep(sleep_time)
                print "SAY:",voice,saytxt,sleep_time
                ph.say_text_in_voice(saytxt,voice)
                    
                # need to run file in entirety, then check for timeout
                elap = datetime.now()-starttime
                if run_sec > 0 and elap.total_seconds() >= run_sec:
                    print "Total time:",elap,"seconds"
                    sys.exit(0)


