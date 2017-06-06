#!/usr/bin/python

import sys, getopt

def main(argv):
    domoticz_host = 'localhost'
    domoticz_port = '8080'

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

    fetch_url = "http://" + domoticz_host + ":" + domoticz_port + "/json.htm?type=hardware"
    print fetch_url

if __name__ == "__main__":
    main(sys.argv[1:])

sys.exit(2)

import urllib, json
url = "http://192.168.2.104:8080/json.htm?type=hardware"
response = urllib.urlopen(url)
data = json.loads(response.read())
print data
