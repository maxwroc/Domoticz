#!/usr/bin/python3

import sys
import getopt
import pprint
import logging

from domoticz import Server
from pyHS100 import TPLinkSmartHomeProtocol

_LOGGER = logging.getLogger(__name__)
# output log info messages to console
_LOGGER.addHandler(logging.StreamHandler(sys.stdout))

domoticz_host = 'localhost'
domoticz_port = '8080'
hardware_name = "SmartPlug"

def main(argv):
    global domoticz_host
    global domoticz_port
    try:
        opts, args = getopt.getopt(argv, "hid:p:")
    except getopt.GetoptError:
        print_help()
        return

    for opt, arg in opts:
        if opt == "-h":
            print_help()
            return
        elif opt == "-d":
            domoticz_host = arg
        elif opt == "-p":
            domoticz_port = arg
        elif opt == "-i":
            install()
            return

def print_help():
    """ Prints help
    """
    print("%s -d <domoticz_host> -p <domoticz_port> -i" % __name__)
    print("  i - Installs local devices on server")
    print("  d - Domoticz host/ip (default: %s)" % domoticz_host)
    print("  p - Domoticz port (default: %s)" % domoticz_port)
    return

def install():
    """ Discovers devices in the local network and installs them on Domoticz server
    """
    # log to explicit file
    logging.basicConfig(filename="installer.log", level=logging.DEBUG)

    _LOGGER.info("Running installer")
    _LOGGER.info("Checking domoticz server configuration")
    server = Server(domoticz_host, domoticz_port)
    _LOGGER.info("  Try to get existing virtual hardware:")
    hardware = server.get_hardware_obj("Name", hardware_name)
    if hardware:
        _LOGGER.info("    found (ID:%s)", hardware.idx)
    else:
        _LOGGER.info("not found")
        _LOGGER.info("  Creating new virtual hardware:")
        hardware = server.create_virtual_hardware(hardware_name)
        if hardware:
            _LOGGER.info("    created")
        else:
            _LOGGER.info("    failed")
            return

    _LOGGER.info("  Getting installed devices")
    devices = hardware.get_devices()
    if devices:
        for device in devices:
            _LOGGER.info(
                "    Found device: %s (%s) %s",
                device.idx, device.data["Type"], device.data["Description"])
    else:
        _LOGGER.info("    Devices not found")

    print("Discovering devices in your local network...")
    network_devices = TPLinkSmartHomeProtocol.discover()
    for dev in network_devices:
        _LOGGER.info(
            "  Found device: %s (%s)",
            dev["ip"],
            dev["sys_info"]["system"]["get_sysinfo"]["alias"])

if __name__ == "__main__":
    main(sys.argv[1:])
