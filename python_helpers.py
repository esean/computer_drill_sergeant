#!/usr/bin/env python
import re, sys, os
import time
import subprocess
import socket
import os.path
import shutil
import datetime
# uncomment to debug in gdb-style debugger
#import pdb
#pdb.set_trace()
import platform

DEBUG = 0

# TODO: all functions need to consider 'ret' from run_subprocess() to know if cmd worked or not

#-----------------------------------
def die(str):
    msg_txt = "FATAL ERROR: %s !\n\nPATH = %s\n\n" % (str,os.environ['PWD'])
    print "\n%s\n" % msg_txt
    sys.exit(1)

#-----------------------------------
def warn(str):
    print "\nWARNING:%s !\n" % str

#-----------------------------------
def log(str):
    print "[%s]LOG:%s..." % (sys.argv[0],str)

#-----------------------------------
def rm(fn):
    if os.path.isfile(fn):
        print "INFO: removing file:%s" % fn
        os.remove(fn)
    else:
        warn("ph.rm(%s) tried to remove but it didn't exist" % fn)
    return None

#----------------------------------
def get_now_datestring():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")

#-----------------------------------
def is_linux():
    if "Linux" in platform.system():
        return True
    else:
        return False

#-----------------------------------
def say_text_in_voice(message,voice,rate=150,pitch=100):
    """
    Enhanced text-to-speech function with dynamic emphasis based on punctuation and text patterns.
    
    Features:
    - Progressive emphasis for multiple exclamation marks (!, !!, !!!, etc.)
    - Different handling for questions (?, ??, ???)
    - Special effects for interrobang (!? or ?!)
    - ALL CAPS word detection for emphasis
    - Ellipsis (...) for dramatic pauses
    - Dash pauses ( - or -- )
    - Repeated letter detection (Noooo!)
    - Dramatic keyword emphasis
    """
    #cmd = "say %s" % (message)
    print "%s" % message
    
    # Base parameters
    amp = 100      # Amplitude (volume) - increased base from 80
    cap = 20       # Capital letter emphasis
    spd = 160      # Speed (words per minute)
    pth = 50       # Pitch - default pitch
    gap = 0        # Gap between words (ms)
    
    # Count exclamation marks for progressive emphasis
    exclamation_count = message.count('!')
    if exclamation_count > 0:
        # Progressive emphasis based on number of exclamations
        amp = min(200 + (exclamation_count * 30), 500)  # Max amplitude 500
        cap = min(30 + (exclamation_count * 15), 100)   # Max capital emphasis 100
        pth = min(50 + (exclamation_count * 10), 99)    # Max pitch 99
        gap = min(exclamation_count * 10, 50)           # Add dramatic pauses
        
    # Handle questions with emphasis
    if '?' in message:
        spd = 140 if exclamation_count == 0 else 120   # Slower for questions
        pth = min(pth + 20, 99)                         # Higher pitch for questions
        
    # Special handling for interrobang (!? or ?!)
    if ('!?' in message or '?!' in message):
        amp = min(amp + 50, 500)
        spd = 130
        gap = max(gap, 20)
        
    # Detect ALL CAPS words for extra emphasis
    words = message.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 1]
    if caps_words:
        cap = min(cap + (len(caps_words) * 10), 100)
        amp = min(amp + 20, 500)
        
    # Handle ellipsis for dramatic effect
    if '...' in message:
        gap = max(gap, 15)  # Add pauses for ellipsis
        spd = max(spd - 20, 100)  # Slow down for dramatic effect
    
    # Handle multiple question marks for extra confusion/urgency
    question_count = message.count('?')
    if question_count > 1:
        pth = min(pth + (question_count * 5), 99)
        spd = max(spd - (question_count * 10), 100)
        
    # Handle dashes for dramatic pauses
    if ' - ' in message or ' -- ' in message:
        gap = max(gap, 25)
        
    # Detect repeated letters for emphasis (e.g., "Noooo!")
    repeated_pattern = re.findall(r'(\w)\1{2,}', message.lower())
    if repeated_pattern:
        spd = max(spd - 30, 80)  # Slow down for repeated letters
        amp = min(amp + 30, 500)  # Increase volume
        
    # Special dramatic keywords
    dramatic_words = ['wait', 'stop', 'no', 'yes', 'help', 'now', 'quick', 'hurry']
    message_lower = message.lower()
    for word in dramatic_words:
        if word in message_lower:
            amp = min(amp + 10, 500)
            break
    
    # Escape the message for shell safety
    escaped_message = message.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
    
    if is_linux():
        # Enhanced espeak command with all parameters
        # -a: amplitude (volume)
        # -s: speed in words per minute  
        # -p: pitch (0-99)
        # -k: capital letter emphasis
        # -g: gap between words in ms
        # -z: remove trailing silence
        cmd = "echo \"%s\" | espeak -v %s -a %d -s %d -p %d -k%d -g %d -z" % (
            escaped_message, voice, amp, spd, pth, cap, gap)
    else:
        # For non-Linux, include amplitude and speed
        cmd = "espeak -v %s -a %d -s %d -p %d \"%s\"" % (voice, amp, spd, pth, escaped_message)
    
    (ret,txt) = run_subprocess(cmd)
    if ret is not 0:
        print "ERROR:say_text_in_voice(%s,%s):%s" % (message,voice,txt)
    return ret

#-----------------------------------
# RETURNS: string containing outward-facing IP address
def get_my_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  ip = s.getsockname()[0]
  s.close()
  return ip

#-----------------------------------
def xlate_CR_to_br(txt):
    return txt.replace('\n',"<br>")
#-----------------------------------
# NOTE: don't call die() from here, since it could go recursive...
def send_email(operator_email,subj_txt,msg_txt):
  my_ip = get_my_ip()
  msg = u""">><br>>><br>'%s'<br><<<br><<<br>""" % (xlate_CR_to_br(msg_txt))
  cmdtxt = "send_email_to.py %s \"%s\" \"%s\"" % (operator_email,subj_txt,msg)
  (ret,txt) = run_subprocess(cmdtxt)
  if ret is not 0:
# NO!!    die("send_email():%s returned failure %d" % (cmdtxt,ret))
     print "FATAL ERROR: send_email():CMD='%s' returned failure %d" % (cmdtxt,ret)
     sys.exit(1)
  return None

#-----------------------------------
# NOTE: don't call die() from here, since it could go recursive...
def old_send_email(operator_email,subj_txt,msg_txt):
  subj = "%s" % subj_txt
  my_ip = get_my_ip()
  msg = u"""%s""" % msg_txt
  cmdtxt = "send_email_to.py %s \"%s\" \"%s\"" % (operator_email,subj,msg)
  (ret,txt) = run_subprocess(cmdtxt)
  if ret is not 0:
     print "FATAL ERROR: send_email():CMD='%s' returned failure %d:%s" % (cmdtxt,ret,txt)
     sys.exit(1)
  return None

#-----------------------------------
def xlate_CR_to_br(txt):
    return txt.replace('\n',"<br>")

#-----------------------------------
def copy_file_to_dest(src,dst):
  srcbase = os.path.basename(src)
  dst_fn = "%s/%s" % (dst,srcbase)
  print "# DBG: copy_file_to_dest: cp src=%s dst=%s" % (src,dst_fn)
  if not os.path.isdir(dst):
    die("copy_file_to_dest(%s,%s) but dest is not directory" % (src,dst))
  shutil.copyfile(src,dst_fn)
  return None

#-----------------------------------
def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

#-----------------------------------
def config_read_key_value(cfgfile,key):
  if not os.path.isfile(cfgfile):
    die("config_read_key_value(%s,%s):cfg file not found" % (cfgfile,key))
  cmdtxt = "readset_inicfg.py -f %s -r %s" % (cfgfile,key)
  (ret,txt) = run_subprocess(cmdtxt)
  if ret is not 0:
      die("config_read_key_value(%s,%s):%s returned failure %d" % (cfgfile,key,cmdtxt,ret))
#  if not txt:
#      die("config_read_key_value(%s,%s) returned a NULL string" % (cfgfile,key))
#  print "# CFG: %s = %s" % (key,txt)
  return txt

#-----------------------------------
def kill_system_processname(processname):
    txt = "pkill %s" % processname
    (ret,res) = run_subprocess(txt)
    time.sleep(5)
    txt = "pkill -9 %s" % processname
    (ret,res) = run_subprocess(txt)

#-----------------------------------
# find first process with name processname, return it's process ID
def find_system_processname_processID(processname):
    # find process ID for this user
    txt = "ps -e -U `whoami` | grep %s | grep -v 'grep %s' | head -n 1 | awk '{print $1}'" % (processname,processname)
    (ret,res) = run_subprocess(txt)
    if ret is not 0:
        return None
    return res.isdigit()

#-----------------------------------
def wait_for_processname_to_START(processname):
    cnt=0
    while True:
        pid = find_system_processname_processID(processname)
        if pid:
            time.sleep(7)	# make sure it fully up...
            return pid
        else:
            cnt+=1
            if cnt > 120:    # wait 2min, 3sec * 40
                die("Could not START processname %s" % processname)
            time.sleep(1)

#-----------------------------------
def wait_for_processname_to_STOP(processname):
    cnt=0
    while True:
        pid = find_system_processname_processID(processname)
        if pid:
            cnt+=1
            if cnt > 120:     # wait 2min, 3sec * 40
                die("Could not STOP processname %s" % processname)
            time.sleep(1)
        else:
            time.sleep(5)
            return None

#-----------------------------------
def stop_app(app_name):
  # if MM is open, close it. then open MM
  kill_system_processname(app_name)
  wait_for_processname_to_STOP(app_name)  # kill MM, wait...
  time.sleep(5)

#-----------------------------------
# RETURNS 0 on success
def run_subprocess(cmdtxt,runCmdInBackground = False):
  global DEBUG
  if DEBUG:
    print "\n# DBG:SUBPROCESS:%s(%d)" % (cmdtxt,runCmdInBackground)
  # if we want to run in the background, just launch the cmd and return
  #---------
  if runCmdInBackground:
    os.system("%s &" % cmdtxt)
    return (0,"No output from background os.system(%s) call" % cmdtxt)
  # else this is a blocking call, use Popen
  #---------
  try:
    p = subprocess.Popen(cmdtxt, stdout=subprocess.PIPE, shell=True,stderr=subprocess.STDOUT)
  except KeyboardInterrupt:
#    print "...got ctrl-c..."
    pid = p.pid
    p.terminate()
    p.send_signal(signal.SIGKILL)
    # Check if the process has really terminated & force kill if not.
    try:
        os.kill(pid, signal.SIGKILL)
        p.kill()
        print "Forced kill"
    except OSError, e:
        print "Terminated gracefully"
  
  (output, err) = p.communicate()
  p_status = p.wait()
  outtxt = output.strip()
  if DEBUG == 1:
    print "# >>>> SUBPROCESS_INFO_START(%s) >>>>" % cmdtxt
    app = cmdtxt.split(' ', 1)[0]
    for ln in outtxt.splitlines():
      print " +%s+> %s" % (app,ln)
    print "# <<<< SUBPROCESS_INFO_END(%s) <<<< " % cmdtxt
    print "# DBG:  SUBPROCESS END:%s retcode=%d" % (cmdtxt,p_status)
  if p_status > 0:
    print "ERROR: error returned from following command,"
    print "ERROR:      $ ",cmdtxt
  return (p_status,outtxt)



###################
# Compute linear regression slope & intercept from passed in CSV file of datapoints
#
# slope = (N * sum(xy) - sum(x)*sum(y)) / (N * sum(x^2) - sum(x)^2)
# intercept = (sum(y) - b*sum(x)) / N
class xy_slope:
    def __init__(self,save_filename,history):
        self._clear()
        self.history = history
        self.saveFn = save_filename
        if os.path.exists(self.saveFn):
          os.remove(self.saveFn)
    
    #--------
    # PUBLIC
    #--------
    def new_sample(self,x,y):
        # just append values to CSV file, this file is then read to get slope/intercept
        with open(self.saveFn, 'a') as the_file:
          the_file.write('%0.12f,%0.12f\n' % (x,y))

    # pull 'history' lines from the 'saveFile', compute slope/intercept from only those
    def get_slope_intercept(self):
        self._clear()
        lines = self._tail(self.saveFn,self.history)
        for line in lines:
          a = re.match('(.*),(.*)',line)
          if a:
            xin = float(a.group(1))
            yin = float(a.group(2))
            self._add_sample(xin,yin)
        if self.N == 0:
            return (0,0)
        if (self.N*self.sum_x2 - self.sum_x*self.sum_x) == 0:
            return (0,0)
        slope = (self.N*self.sum_xy - self.sum_x*self.sum_y) / (self.N*self.sum_x2 - self.sum_x*self.sum_x)
        intercept = (self.sum_y - slope*self.sum_x) / self.N
        return (slope,intercept)

    # y = mx + b
    def get_y_value_given_x(self,x):
        (m,b) = self.get_slope_intercept()
        return (m * x) + b
    # x = (y - b)/m
    def get_x_value_given_y(self,y):
        (m,b) = self.get_slope_intercept()
        return (y - b) / m;
    
    #--------
    # PRIVATE
    #--------
    def _clear(self):
        self.N = self.sum_xy = self.sum_x = self.sum_y = self.sum_x2 = 0
    
    def _add_sample(self,x,y):
        self.N += 1
        self.sum_xy += x * y
        self.sum_x += x
        self.sum_y += y
        self.sum_x2 += x * x

    def _tail(self,fn,n):
        stdin,stdout = os.popen2('tail -n %d %s' % (n,fn))
        stdin.close()
        lines = stdout.readlines(); stdout.close()
        return lines

def get_tempfile(nm):
  stdin,stdout = os.popen2('mktemp /tmp/%s.XXXXXXXXX' % (nm))
  stdin.close()
  tmpfn = stdout.readlines(); stdout.close()
  return tmpfn[0].rstrip()
###################



#-----------------------------------
class Point:
  """ Create a new Point, at coordinates x, y, z """
  def __init__(self, x=0, y=0, z=0):
      """ Create a new point at x, y, z """
      self.x = x
      self.y = y
      self.z = z
  def distance_from_origin(self):
      """ Compute my distance from the origin """
      return ((self.x ** 2) + (self.y ** 2) + (self.z ** 2)) ** 0.5
  def to_string(self):
      return "({0}, {1}, {2})".format(self.x, self.y, self.z)
  def halfway(self, target):
     """ Return the halfway point between myself and the target """
     mx = (self.x + target.x)/2
     my = (self.y + target.y)/2
     mz = (self.z + target.z)/2
     return Point(mx, my, mz)
  def minus(self,target):
     mx = (self.x - target.x)
     my = (self.y - target.y)
     mz = (self.z - target.z)
     return Point(mx, my, mz)
  def angleBetweenVector(self,vB):
    vA = Point(self.x,self.y,self.z)
    fCrossX = vA.y * vB.z - vA.z * vB.y
    fCrossY = vA.z * vB.x - vA.x * vB.z
    fCrossZ = vA.x * vB.y - vA.y * vB.x
    fCross = math.sqrt(fCrossX * fCrossX + fCrossY * fCrossY + fCrossZ * fCrossZ)
    fDot = vA.x * vB.x + vA.y * vB.y + vA.z + vB.z
    return math.atan2(fCross, fDot)




