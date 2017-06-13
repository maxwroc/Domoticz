#!/usr/bin/python3

import sys
import getopt
import logging
import os

from installer import install
from pyHS100 import TPLinkSmartHomeProtocol

_LOGGER = logging.getLogger(__name__)
# output log info messages to console
_LOGGER.addHandler(logging.StreamHandler(sys.stdout))

def main(argv):
    """ Main
    """
    domoticz_host = "localhost"
    domoticz_port = "8080"
    hardware_name = "SmartPlug"

    try:
        opts, args = getopt.getopt(argv, "hids:p:")
    except getopt.GetoptError:
        print_help(domoticz_host, domoticz_port)
        return

    run_installation = False
    for opt, arg in opts:
        if opt == "-h":
            print_help(domoticz_host, domoticz_port)
            return
        elif opt == "-s":
            domoticz_host = arg
        elif opt == "-p":
            domoticz_port = arg
        elif opt == "-i":
            run_installation = True
        elif opt == "-d":
            discover()
            return

    if run_installation:
        install(_LOGGER, domoticz_host, domoticz_port, hardware_name)

def print_help(domoticz_host, domoticz_port):
    """ Prints help
    """
    print()
    print("%s -s <domoticz_host> -p <domoticz_port> -i" % os.path.basename(__file__))
    print("  i - Performs installation")
    print("  s - Domoticz server host/ip (default: %s)" % domoticz_host)
    print("  p - Domoticz port (default: %s)" % domoticz_port)

def discover():
    """ Finds devices in local network
    """
    print()
    print("Discovering devices in your local network")
    for dev in TPLinkSmartHomeProtocol.discover():
        print(
            "  Found device: %s (%s)" %
            (dev["ip"], dev["sys_info"]["system"]["get_sysinfo"]["alias"]))

if __name__ == "__main__":
    main(sys.argv[1:])
