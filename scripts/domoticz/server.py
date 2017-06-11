import json
import urllib.request

def fetch_json(host, port, query):
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

    if response is None:
        raise ValueError("Getting response from host failed: " + url)

    parsed_result = json.loads(response.read())
    if parsed_result["status"] != "OK":
        raise ValueError("Invalid response from server", parsed_result)

    return parsed_result

def get_object_with_property_value(collection, name, value):
    """ Returns first object, from given collection, which has a property with given value.

    :param collection: Collection to search.
    :param name: Property name which value should be checked.
    :param value: Value to match.
    :return: Object
    """
    for obj in collection:
        if obj[name] == value:
            return obj
    return

class Server:
    """ Server class exposigng API requests as functions.
    """
    host = "localhost"
    port = "8080"

    def __init__(self, host="localhost", port="8080"):
        self.host = host
        self.port = port

    def get_all_devices(self):
        """ Gets a list of all available devices on server.

        :return: List of devices
        :rtype: array
        """
        return self.fetch("type=devices&filter=all&used=true")["result"]

    def get_devices_for_hardware(self, hardware_id):
        """ Gets a list of devices assigned to given hardware.

        :param hardware_id: Hardware ID.

        :return: List of devices
        :rtype: array
        """
        result = self.get_all_devices()
        return [
            device
            for device in result["result"]
            if "HardwareID" in device and device["HardwareID"] == hardware_id]

    def get_all_hardware(self):
        """ Gets a list of all hardware installed on server.

        :return: List of hardware.
        :rtype: array
        """
        return self.fetch("type=hardware")["result"]

    def get_hardware(self, property_name, property_value):
        """ Gets hardware object with given property value.

        :param property_name: Property name which value should be searched for.
        :param property_value: Value which should match.

        :return: Hardware object.
        :rtype: object
        """
        return get_object_with_property_value(
            self.get_all_hardware(),
            property_name,
            property_value)

    def create_virtual_hardware(self, name):
        """ Creates new virtual hardware.

        :param name: Name of the hardware.

        :return: Created hardware.
        :rtype: object
        """
        # check if such hardware does not exist already
        existing_hardware = self.get_hardware("Name", name)
        if existing_hardware is not None:
            raise ValueError(
                "Hardware with given name exists already [" + existing_hardware["idx"] + "]")

        # send a request to create hardware
        self.fetch("type=command&param=addhardware&htype=15&port=0&name=" + name + "&enabled=true")

        # double check if it was created
        existing_hardware = self.get_hardware("Name", name)
        if existing_hardware is None:
            raise ValueError("Failed to create new hardware")

        return existing_hardware

    def delete_hardware(self, hardware_id=None, name=None):
        """ Deletes hardware with given ID or name.

        :param id: Hardware ID.
        :param name: Name of the hardware.
        :return: None
        """

        if hardware_id is None and name is None:
            raise ValueError("Failed to delete hardware. No hardware id or name passed.")

        if hardware_id is None and name is not None:
            # we need to find the hardware with given name to get it's ID
            hardware = self.get_hardware("Name", name)
            if hardware is None:
                raise ValueError("Failed to delete hardware with given name: " + name)

            hardware_id = hardware["idx"]

        self.fetch("type=command&param=deletehardware&idx=" + str(hardware_id))

    def fetch(self, query):
        """ Fetches JSON data from server for a given query text.
        :param query: Url query string.
        :return: Server response.
        :rtype: json
        """
        return fetch_json(self.host, self.port, query)
