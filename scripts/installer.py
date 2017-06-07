#!/usr/bin/python

import sys, getopt, urllib, json

domoticz_host = 'localhost'
domoticz_port = '8080'
hardware_name = "SmartPlug"

def fetchJson(path):
    url = "http://" + domoticz_host + ":" + domoticz_port + path
    response = urllib.urlopen(url)

    if response == None:
        raise ValueError("Getting response from host failed: " + url)

    parsedResult = json.loads(response.read())
    if parsedResult["status"] != "OK":
        raise ValueError("Invalid response from server", parsedResult)

    return parsedResult

def getObjectWithProperty(array, name, value):
    for obj in array:
        if obj[name] == value:
            return obj
    return

def createHardware():
    fetchJson("/json.htm?type=command&param=addhardware&htype=15&port=0&name=" + hardware_name + "&enabled=true")
    result = fetchJson("/json.htm?type=hardware")

    obj = getObjectWithProperty(data["result"], "Name", "SmartPlug")
    if obj == None:
        raise ValueError("Failed to create new hardware")

    return obj


def main(argv):
    global domoticz_host, domoticz_port
    try:
        opts, args = getopt.getopt(argv, "hd:p:")
    except getopt.GetoptError:
        print 'install.py -d <domoticz_host> -p <domoticz_port>'
    
    for opt, arg in opts:
        if opt == "-h":
            print 'install.py -d <domoticz_host> -p <domoticz_port>'
            sys.exit(2)
        elif opt == "-d":
            domoticz_host = arg
        elif opt == "-p":
            domoticz_port = arg

    data = fetchJson("/json.htm?type=hardware")
    smartPlug = getObjectWithProperty(data["result"], "Name", hardware_name)

    if smartPlug == None:
        print "Creating new hardware for SmartPlug"
        smartPlug = createHardware()
    else:
        print "Hardware for SmartPlug exists already - reusing"   



if __name__ == "__main__":
    main(sys.argv[1:])
    
