#!/usr/bin/env python
#
# Magnus Strahlert @ 171020
#   Checks if ssl certificate is about to expire with Nagios support

import string
import getopt
import os
import sys
from datetime import datetime
from subprocess import PIPE, Popen

def cmdline(command):
  process = Popen(args = command, stdout = PIPE, shell = True)
  return process.communicate()[0]

def usage():
  print """
Checks if ssl certificate is about to expire

Usage: sslcert [options]
where options is one or more of the following:

  --host <host>     : the hostname to connect to that runs the ssl service
  --port <port>     : the portnumber to connect to
  --nagios          : support Nagios in output
  --critical <days> : days until expiry to show as critical
  --warning <days>  : days until expiry to show as warning
"""

def main():
  try:
    opts, remainder = getopt.getopt(sys.argv[1:], "h", ["help", "host=", "port=", "nagios", "critical=", "warning="])
  except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

  # Defaults
  #######################
  port = 443
  host = False
  nagios = False
  critical = False
  warning = False
  #######################

  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt == "--host":
      host = arg
    elif opt == "--port":
      try:
        port = int(arg)
      except ValueError:
        print "Error: port must be a number, reverting to default (%d)" % port
    elif opt == "--nagios":
      nagios = True
    elif opt == "--critical":
      try:
        critical = int(arg)
      except ValueError:
        print "Error: critical must a number, reverting to default to not show"
    elif opt == "--warning":
      try:
        warning = int(arg)
      except ValueError:
        print "Error: warning must a number, reverting to default to not show"
    else:
      assert False, "unhandled option"

  if host == False:
    print "Error: Host to connect to must be given"
    sys.exit(2)

  # If critical or warning is given, they must conform to the rules
  if critical > warning:
    print "Error: Critical must be lower than warning"
    sys.exit(2)

  # "openssl s_client" opens a connection and waits for input. By piping an
  # empty string as input, it immediately exits which is what we want. The
  # output is then piped to "openssl x509" to then grep for expiry date.
  output = cmdline("echo|openssl s_client -connect %s:%d 2>/dev/null|openssl x509 -noout -dates|grep notAfter" % (host, port))

  if len(output) == 0:
    print "Check host or port"
    sys.exit(2)

  # Split the output so we only get what we're interested in; the expiry date
  output = output.split('\n', 1)[0]
  output = output.split('=', 1)[1]

  expiry_time = datetime.strptime(output, "%b %d %H:%M:%S %Y %Z")
  days = (expiry_time - datetime.today()).days

  if days < 0:
    result = "have expired"
  elif days == 0:
    result = "will expire today"
  #elif days < 400:
  else:
    result = "will expire in %d day" % days

  # grammar :)
  if days > 1:
    result += "s"

  result = "Certificate for https://%s:%d/ %s" % (host, port, result)

  # Critical and warning only makes sense when used in Nagios check
  if critical and days < critical:
    if nagios:
      result = "CRITICAL - %s" % result
    exit_value = 2
  elif warning and days < warning:
    if nagios:
      result = "WARNING - %s" % result
    exit_value = 1 
  else:
    if nagios:
      result = "OK - %s" % result
    # This will be the default exit_value
    exit_value = 0

  print result
  sys.exit(exit_value)

  #print str(epoch_time)
  #print str(current_time)

if __name__ == "__main__":
  main()
