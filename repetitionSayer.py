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
    print "%s -v [voice] -f [program file to run] {-g [second file]} {-t [run X seconds]} {-r}" % os.path.basename(sys.argv[0])
    print
    print "Runs [program file] line-by-line and either sleeps, or says something"
    print "If a second file is provided with -g, alternates between the two files"
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
    print "Or, use '-r' param to read lines randomly instead of sequentially"
    print
    print "Example"
    print "     $ ./repetitionSayer.py -f file -a 2 -s 8 -t 60"
    print "     $ ./repetitionSayer.py -f file1 -g file2 -a 2 -s 8 -t 60"
    print "     $ ./repetitionSayer.py -f file -r -a 2 -s 8 -t 60"
    print

#----------------------------------
if __name__ == '__main__':

    voice = "english-north" # Yuna" #"Kyoko"
    filenm = str()
    filenm2 = str()  # Second file name
    run_sec = 0
    rand_start = 3.0
    rand_stop = 20.0
    random_mode = False  # Flag for random line reading
    
    try:
        opts, args = go.getopt(sys.argv[1:], "hv:f:g:t:a:s:lr", ["help", "voice=", "program_script_filename=", "second-file=", "run_sec=", "rand-time-start=", "rand-time-stop=", "list-voices", "random" ])
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
        elif option in ('-g', '--second-file'):
            filenm2 = str(argument)
        elif option in ('-t', '--run_sec'):
            run_sec = float(argument)
        elif option in ('-a', '--rand-time-start'):
            rand_start = float(argument)
        elif option in ('-s', '--rand-time-stop'):
            rand_stop = float(argument)
        elif option in ('-l', '--list-voices'):
            cmd = "espeak -v ?"
            (ret,txt) = ph.run_subprocess(cmd)
            print txt
            sys.exit(0)
        elif option in ('-r', '--random'):
            random_mode = True
    if not voice or not filenm:
        usage()
        ph.die("Incorrect params")

    starttime = datetime.now()
    
    def process_line(ln, voice, rand_start, rand_stop):
        """Process a single line from the file"""
        ln = ln.rstrip()
        if ln.startswith('#'):
            return False  # Skip comment
        
        row = re.split(',',ln,2)
        if 'randsmall' in str(row[0]):
            sleep_time = random.uniform(0, rand_start)
        elif 'rand' in str(row[0]):
            sleep_time = random.uniform(rand_start, rand_stop)
        else:
            sleep_time = float(row[0])
        saytxt = str(row[1])
        print "row=",row," say=",saytxt

        time.sleep(sleep_time)
        print "SAY:v=",voice," s=",saytxt,sleep_time
        ph.say_text_in_voice(saytxt,voice)
        return True
    
    # If no second file, use original behavior
    if not filenm2:
        while True:
            with open(filenm, 'r') as in_file:
                # Read all lines
                lines = [ln for ln in in_file]
                
                # Shuffle if random mode is enabled
                if random_mode:
                    random.shuffle(lines)
                
                for ln in lines:
                    if process_line(ln, voice, rand_start, rand_stop):
                        # Check timeout after processing each line
                        elap = datetime.now()-starttime
                        if run_sec > 0 and elap.total_seconds() >= run_sec:
                            print "Total time:",elap,"seconds"
                            sys.exit(0)
    else:
        # Alternate between two files
        while True:
            with open(filenm, 'r') as file1, open(filenm2, 'r') as file2:
                # Read all lines from both files
                lines1 = [ln for ln in file1]
                lines2 = [ln for ln in file2]
                
                # Shuffle if random mode is enabled
                if random_mode:
                    random.shuffle(lines1)
                    random.shuffle(lines2)
                
                # Determine the maximum number of lines
                max_lines = max(len(lines1), len(lines2))
                
                # Process lines alternating between files
                for i in range(max_lines):
                    # Process line from file1 if available
                    if i < len(lines1):
                        if process_line(lines1[i], voice, rand_start, rand_stop):
                            elap = datetime.now()-starttime
                            if run_sec > 0 and elap.total_seconds() >= run_sec:
                                print "Total time:",elap,"seconds"
                                sys.exit(0)
                    
                    # Process line from file2 if available
                    if i < len(lines2):
                        if process_line(lines2[i], voice, rand_start, rand_stop):
                            elap = datetime.now()-starttime
                            if run_sec > 0 and elap.total_seconds() >= run_sec:
                                print "Total time:",elap,"seconds"
                                sys.exit(0)


