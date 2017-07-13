#! /usr/bin/env python

###############################################################################
# Nagios plugin template 
#
# Notes
# - The RHEL boxes I work on are currently limited to Python 2.6.6, hence the 
#   use of (deprecated) optparse. If I can ever get them all updated to 
#   Python 2.7 (or better yet, 3.3), I'll switch to argparse
# - This template runs in 2.6-3.3. Any changes made will need to be appropriate
#   to the Python distro you want to use
#
###############################################################################

__author__ = 'Gregor Tudan'
__version__= 0.1

from argparse import ArgumentParser
import logging as log
import requests

def main():
    """ Main plugin logic goes here """

    ## Parse command-line arguments
    args = parse_args()

    ## Uncomment to test logging levels against verbosity settings
    # log.debug('debug message')
    # log.info('info message')
    # log.warning('warning message')
    # log.error('error message')
    # log.critical('critical message')
    # log.fatal('fatal message')

    get_waiting_time(args)
    gtfo(0)


def parse_args():
    """ Parse command-line arguments """

    parser = ArgumentParser(usage='usage: %prog [-v|vv|vvv] [options]',
                            epilog='{0}: v.{1} by {2}'.format('%prog', __version__, __author__))

    ## Verbosity (want this first, so it's right after --help and --version)
    parser.add_argument('-v', help='Set verbosity level',
                        action='count', default=0, dest='v')

    ## CLI arguments specific to this script
    group = parser.add_argument_group(parser,'Plugin Options')
    group.add_argument('-i', '--customer-id', help='IDNow Customer id',
                       default=None, dest='customer_id')
    group.add_argument('-k', '--api-key', help='Your IDNow API key',
                       default=None, dest='api_key')
    group.add_argument('-g', '--gateway-host', help='The hostname of the idnow gateway server',
            default='gateway.idnow.de', dest='hostname')
    
    ## Common CLI arguments
    parser.add_argument('-c', '--critical', help='The critical waiting time in seconds. Default: %(default)s',
                      default=600, type=float, dest='crit', metavar='###')
    parser.add_argument('-w', '--warning', help='The threshold waiting time for a warning in seconds. Default: %(default)s',
                      default=300, type=float, dest='warn', metavar='###')
    

    args = parser.parse_args()

    ## Set the logging level based on the -v arg
    log.getLogger().setLevel([log.ERROR, log.WARN, log.INFO, log.DEBUG][args.v])

    log.debug('Parsed arguments: {0}'.format(args))

    return args

def get_waiting_time(args):
    try:
        api_token = get_api_token(args)
        url = get_base_url(args.hostname, args.customer_id)

        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        gtfo(3, "UNKNOWN - ERROR: failed to get status: %s" % err)

    json = r.json()
    log.debug(json)

    # Estimated waiting time in seconds
    estimated_waiting_time = json['estimatedWaitingTime']
    waiting_customers = json['numberOfWaitingChatRequests']

    msg = "Estimated waiting time is {0} seconds. There are {1} people waiting.".format(
             estimated_waiting_time, waiting_customers)

    perf_data = dict(estimated_waiting_time=estimated_waiting_time, waiting_customers=waiting_customers)

    if estimated_waiting_time < args.warn:
        gtfo(0, "OK - " + msg, perf_data)
    elif estimated_waiting_time >= args.crit:
        gtfo(2, "CRITICAL - " + msg, perf_data)
    else:
        gtfo(1, "WARN - " + msg, perf_data)

def get_api_token(args):
    url = get_base_url(args.hostname, args.customer_id) + '/login'
    payload = { 'apiKey': args.api_key }
    r = requests.post(url, json=payload)
    r.raise_for_status()

    json = r.json()
    return json['authToken']
    

def get_base_url(host_name, customer_id):
    return 'https://{0}/api/v1/{1}'.format(host_name, customer_id)


def gtfo(exitcode, message='', perf_data={}):
    """ Exit gracefully with exitcode and (optional) message """

    log.debug('Exiting with status {0}. Message: {1}'.format(exitcode, message))

    perf_string = ''.join('{0}={1} '.format(key, val) for key, val in perf_data.items())
    
    if message:
        print("%s | %s" % (message, perf_string))
    exit(exitcode)

if __name__ == '__main__':
    ## Initialize logging before hitting main, in case we need extra debuggability
    log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()
