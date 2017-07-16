#! /usr/bin/env python
"""
Check the estimated waiting time for an identification

This estimate is done by IDNow using the average of a 10 minute sliding
window, rounded to about 15 second intervals and adding a small buffer.

The estimates seem to take your booked SLA times into account when calculating
a default (in case there were no customers in the last 10 minutes).

In their API-Documentation IDNow makes clear that this is not to be taken
as performance indicator or measurement of their SLA times.
"""

from argparse import ArgumentParser
import logging as log
import requests

__author__ = 'Gregor Tudan'
__version__ = 0.1


def main():
    """ Main plugin logic goes here """

    # Parse command-line arguments
    args = parse_args()

    get_waiting_time(args)
    gtfo(0)


def parse_args():
    """ Parse command-line arguments """

    parser = ArgumentParser(usage='usage: %prog [-v|vv|vvv] [options]',
                            epilog='{0}: v.{1} by {2}'.format('%prog', __version__, __author__))

    # Verbosity (want this first, so it's right after --help and --version)
    parser.add_argument('-v', help='Set verbosity level',
                        action='count', default=0, dest='v')

    # CLI arguments specific to this script
    group = parser.add_argument_group(parser, 'Plugin Options')
    group.add_argument('-i', '--customer-id', help='IDNow Customer id',
                       default=None, dest='customer_id')
    group.add_argument('-k', '--api-key', help='Your IDNow API key',
                       default=None, dest='api_key')
    group.add_argument('-g', '--gateway-host', help='The hostname of the idnow gateway server',
                       default='gateway.idnow.de', dest='hostname')

    # Common CLI arguments
    parser.add_argument('-c', '--critical',
                        help='The critical waiting time in seconds. Default: %(default)s',
                        default=600, type=float, dest='crit', metavar='###')
    parser.add_argument('-w', '--warning',
                        help='The threshold waiting time for a warning in seconds. Default: %(default)s',
                        default=300, type=float, dest='warn', metavar='###')

    args = parser.parse_args()

    # Set the logging level based on the -v arg
    log.getLogger().setLevel([log.ERROR, log.WARN, log.INFO, log.DEBUG][args.v])

    log.debug('Parsed arguments: %s', args)

    return vars(args)


def get_waiting_time(args):
    """ Get the current estimated waiting time"""
    try:
        url = get_base_url(args['hostname'], args['customer_id'])

        request = requests.get(url)
        request.raise_for_status()
    except requests.exceptions.RequestException as err:
        gtfo(3, "UNKNOWN - ERROR: failed to get status: %s" % err)

    json = request.json()
    log.debug(json)

    # Estimated waiting time in seconds
    estimated_waiting_time = json['estimatedWaitingTime']
    waiting_customers = json['numberOfWaitingChatRequests']

    msg = "Estimated waiting time is {0} seconds. There are {1} people waiting.".format(
        estimated_waiting_time, waiting_customers)

    perf_data = {
        'estimated_waiting_time': estimated_waiting_time,
        'waiting_customers': waiting_customers
    }

    if estimated_waiting_time < args['warn']:
        gtfo(0, "OK - " + msg, perf_data)
    elif estimated_waiting_time >= args['crit']:
        gtfo(2, "CRITICAL - " + msg, perf_data)
    else:
        gtfo(1, "WARN - " + msg, perf_data)


def get_api_token(args):
    """ Get an API token from IDNow - the current api for the estimated waiting time
        does not seem to require authentication. """
    url = get_base_url(args['hostname'], args['customer_id']) + '/login'
    payload = {'apiKey': args['api_key']}
    request = requests.post(url, json=payload)
    request.raise_for_status()

    json = request.json()
    return json['authToken']


def get_base_url(host_name, customer_id):
    """
    :arg host_name: the host name of the IDNow gateway server
    :arg customer_id: your customer id
    :returns the base url of the IDNow API and the selected customer
    """
    return 'https://{0}/api/v1/{1}'.format(host_name, customer_id)


def gtfo(exitcode, message='', perf_data=None):
    """ Exit gracefully with exitcode and (optional) message """

    if perf_data is None:
        perf_data = {}
    log.debug('Exiting with status %s. Message: %s', exitcode, message)

    perf_string = ''.join('{0}={1} '.format(key, val) for key, val in perf_data.items())

    if message:
        print("%s | %s" % (message, perf_string))
    exit(exitcode)


if __name__ == '__main__':
    # Initialize logging before hitting main, in case we need extra debug info
    FORMAT = '%(asctime)s - %(funcName)s - %(levelname)s - %(message)s'
    log.basicConfig(level=log.DEBUG, format=FORMAT)
    main()
