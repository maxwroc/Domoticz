#!/usr/bin/python3

import sys
import getopt
import pprint
import domoticz

from pyHS100 import TPLinkSmartHomeProtocol

domoticz_host = 'localhost'
domoticz_port = '8080'
hardware_name = "SmartPlug"

def main(argv):
    global domoticz_host
    global domoticz_port
    try:
        opts, args = getopt.getopt(argv, "htd:p:")
    except getopt.GetoptError:
        print('install.py -d <domoticz_host> -p <domoticz_port>')

    for opt, arg in opts:
        if opt == "-h":
            print('install.py -d <domoticz_host> -p <domoticz_port>')
            sys.exit(2)
        elif opt == "-d":
            domoticz_host = arg
        elif opt == "-p":
            domoticz_port = arg
        elif opt == "-t":
            return

    server = domoticz.Server(domoticz_host, domoticz_port)

    hardware = server.get_hardware_obj("Name", hardware_name)
    if not hardware:
        hardware = server.create_virtual_hardware(hardware_name)

    devices = hardware.get_devices()
    if not devices:
        print("Devices not found")
        return

    for device in devices:
        print("Found device: " + device.idx +
              " (" + device.data["Type"] + ") " +
              device.data["Description"])

    for dev in TPLinkSmartHomeProtocol.discover():
        print("Found device: %s" % dev["ip"])

if __name__ == "__main__":
    main(sys.argv[1:])
