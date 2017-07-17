# Nagios Check Script for IDNow Waiting Queue

[![Build Status](https://travis-ci.org/gtudan/check_idnow.svg?branch=master)](https://travis-ci.org/gtudan/check_idnow)

This script can monitor the IDNow waiting queue length in terms off expected waiting time and number of customers currently waiting (though the later one is unofficial and not documented in the API reference manual).

## Usage

```
usage: usage: check_idnow.py [-v|vv|vvv] [options]

optional arguments:
  -h, --help            show this help message and exit
  -v                    Set verbosity level
  -c ###, --critical ###
                        The critical waiting time in seconds. Default: 600
  -w ###, --warning ###
                        The threshold waiting time for a warning in seconds.
                        Default: 300

Plugin Options:
  -i CUSTOMER_ID, --customer-id CUSTOMER_ID
                        IDNow Customer id
  -k API_KEY, --api-key API_KEY
                        Your IDNow API key
  -g HOSTNAME, --gateway-host HOSTNAME
                        The hostname of the idnow gateway server

check_idnow v.0.1 by Gregor Tudan
```



