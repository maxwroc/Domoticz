#!/usr/bin/python3

import sys, getopt, pprint, domoticz

domoticz_host = 'localhost'
domoticz_port = '8080'
hardware_name = "SmartPlug"

def main(argv):
    global domoticz_host, domoticz_port
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
    
    smartPlug = server.getHardware("Name", hardware_name)
    if smartPlug == None:
        print("Creating new virtual hardware")
        smartPlug = server.createVirtualHardware(hardware_name)

if __name__ == "__main__":
    main(sys.argv[1:])
    
