import json
import urllib.request
import urllib.parse
import logging

_LOGGER = logging.getLogger(__name__)

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
    _LOGGER.debug("Fetching url: %s", url)
    response = urllib.request.urlopen(url)

    if not response:
        raise ValueError("Getting response from host failed: " + url)

    parsed_result = json.loads(response.read())
    if parsed_result["status"] != "OK":
        msg = "Request did not succeed. "
        if "message" in parsed_result:
            msg += parsed_result["status"] + ": " + parsed_result["message"]
        raise ValueError(msg, parsed_result)

    return parsed_result

class DomoticzApi:
    """ Server class exposigng API requests as functions.
    """
    host = "localhost"
    port = "8080"

    def __init__(self, host="localhost", port="8080"):
        self.host = host
        self.port = port

    def get_all_devices(self, custom_filter=None):
        """ Gets a list of all available devices on server.
        :return: List of devices
        :rtype: list
        """
        result = self.fetch("type=devices&filter=all&used=true")["result"]
        return list(filter(custom_filter, result))

    def get_device(self, property_name, property_value):
        """ Gets a single device with given property value.
        :param property_name: Property name which value should be searched for.
        :param property_value: Value which should match.
        :return: Device data.
        :rtype: json
        """
        query = "type=devices&used=true&order=Name"
        if property_name == "idx":
            query += "&rid=" + str(property_value)

        results = self.fetch(query)["result"]

        results = list(filter(lambda x: x[property_name] == property_value, results))

        if not results:
            return None

        return results[0]

    def get_devices_for_hardware(self, hardware_id):
        """ Gets a list of devices assigned to given hardware.
        :param hardware_id: Hardware ID.
        :return: List of devices
        :rtype: list
        """
        hardware_id = int(hardware_id)
        return self.get_all_devices(
            lambda hw: "HardwareID" in hw and hw["HardwareID"] == hardware_id)

    def get_all_hardware(self, custom_filter=None):
        """ Gets a list of all hardware installed on server.
        :return: List of hardware.
        :rtype: list
        """
        results = self.fetch("type=hardware")["result"]
        return list(filter(custom_filter, results))

    def get_hardware(self, property_name, property_value):
        """ Gets hardware object with given property value.
        :param property_name: Property name which value should be searched for.
        :param property_value: Value which should match.
        :return: Hardware data.
        :rtype: json
        """
        results = self.get_all_hardware(
            lambda hw: property_name in hw and hw[property_name] == property_value)

        if not results:
            return

        return results[0]

    def create_virtual_sensor(self, name, sensor_type, hardware_id):
        """ Creates virtual sensor for given hardware
        :param name: Name of the sensor.
        :param sensor_type: Type of the sensor (int)
        :param hardware_id: Hardware ID.
        """
        self.query(
            type="createvirtualsensor",
            idx=hardware_id,
            sensorname=name,
            sensortype=sensor_type
        )

    def create_virtual_hardware(self, name):
        """ Creates new virtual hardware.
        :param name: Name of the hardware.
        :return: Created hardware data.
        :rtype: json
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

    def update_device(self, idx, name, properties_to_update):
        """ Updates device properties
        """
        # these two are required
        properties_to_update["type"] = "setused"
        properties_to_update["used"] = "true"
        properties_to_update["idx"] = idx
        properties_to_update["name"] = name

        self.query(**properties_to_update)

    def query(self, **params):
        """ Generic method to make a request to server.
        """
        return self.fetch(urllib.parse.urlencode(params))

    def fetch(self, query):
        """ Fetches JSON data from server for a given query text.
        :param query: Url query string.
        :return: Server response.
        :rtype: json
        """
        return fetch_json(self.host, self.port, query)
