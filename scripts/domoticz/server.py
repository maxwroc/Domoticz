

import json, urllib.request

def fetchJson(host, port, query):
    """
    Fetches data from given host and parses it as a JSON. Additionally it validates 
    if the request/response was sucessfult and there were no errors on the server.

    :param host: Host on which Domoticz is running
    :param port: Port on which domoticz is listening
    :param query: Query to be used to fetch the data
    :return: Response JSON
    :rtype: json

    :raises ValueError: When no response from server
    :raises ValueError: When there was an error on the server 
    """
    url = "http://" + host + ":" + port + "/json.htm?" + query
    response = urllib.request.urlopen(url)

    if response == None:
        raise ValueError("Getting response from host failed: " + url)

    parsedResult = json.loads(response.read())
    if parsedResult["status"] != "OK":
        raise ValueError("Invalid response from server", parsedResult)

    return parsedResult

def getObjectWithPropertyValue(array, name, value):
    for obj in array:
        if obj[name] == value:
            return obj
    return

class Server:
    host = "localhost"
    port = "8080"

    def __init__(self, host = "localhost", port = "8080"):
        self.host = host
        self.port = port

    def getAllDevices(self):
        return self.fetch("type=devices&filter=all&used=true")["result"]

    def getDevicesForHardware(self, hardwareId):
        result = self.getAllDevices()
        return [device for device in result["result"] if "HardwareID" in device and device["HardwareID"] == hardwareId]

    def getAllHardware(self):
        return self.fetch("type=hardware")["result"]

    def getHardware(self, propertyName, propertyValue):
        return getObjectWithPropertyValue(
            self.getAllHardware(),
            propertyName,
            propertyValue)

    def createVirtualHardware(self, name):
        # check if such hardware does not exist already
        existingHardware = self.getHardware("Name", name)
        if existingHardware != None:
            raise ValueError("Hardware with given name exists already [" + existingHardware["idx"] + "]")

        # send a request to create hardware
        self.fetch("type=command&param=addhardware&htype=15&port=0&name=" + name + "&enabled=true")

        # double check if it was created
        existingHardware = self.getHardware("Name", name)
        if existingHardware == None:
            raise ValueError("Failed to create new hardware")

        return existingHardware

    def deleteHardware(self, name = None, id = None):
        self.fetch("type=command&param=deletehardware&idx=" + str(id))
    
    def fetch(self, path):
        return fetchJson(self.host, self.port, path)
