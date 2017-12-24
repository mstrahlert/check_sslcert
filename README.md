# check_sslcert

Checks if ssl certificate is about to expire with Nagios support.

Use as a nagios service check against a host and port. Running the program without arguments will show this help.

```Checks if ssl certificate is about to expire
Usage: sslcert [options]
where options is one or more of the following:
  --host <host>     : the hostname to connect to that runs the ssl service
  --port <port>     : the portnumber to connect to
  --nagios          : support Nagios in output
  --critical <days> : days until expiry to show as critical
  --warning <days>  : days until expiry to show as warning
```
