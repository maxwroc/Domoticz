import base64

from .api import DomoticzApi

class Server(DomoticzApi):
    """
    Represents server object. It is an API wrapper which returns objects as function results
    """

    def get_hardware_obj(self, property_name, property_value):
        """ Gets a hardware object.
        :return: Hardware object.
        :rtype: Hardware
        """
        result = self.get_hardware(property_name, property_value)
        if result is None:
            return

        return Hardware(self, data=result)

    def get_all_hardware_objs(self):
        """ Gets a list of all hardware installed on server.
        :return: List of hardware.
        :rtype: Hardware list
        """
        results = self.get_all_hardware()

        if results is None:
            return []

        return [Hardware(self, data=hw) for hw in results]

    def get_device_obj(self, property_name, property_value):
        """ Gets a single device with given property value.
        :param property_name: Property name which value should be searched for.
        :param property_value: Value which should match.
        :return: Device object.
        :rtype: Devic
        """
        result = self.get_device(property_name, property_value)
        if result is None:
            return

        return device_factory(self, result)

class Hardware:
    """ Represents hardware object stored on server.
    :param server: Server instance.
    :param idx: Hardware ID.
    :param data: Hardware JSON data.
    """
    def __init__(self, server_instance, idx=None, data=None):
        self.server = server_instance
        self.idx = idx
        self.data = data

        if data is not None:
            self.idx = data["idx"]
        elif idx is not None:
            self.data = server_instance.get_hardware("idx", idx)
            if self.data is None:
                raise ValueError("Failed to fetch hardware data for ID: " + str(idx))

    def get_devices(self):
        """ Gets all devices from current hardware.
        :return: List of devices.
        :rtype: list
        """
        return self.server.get_devices_for_hardware(self.idx)

class Device:
    """ Represens generic device object.
    :param server: Server instance.
    :param idx: Device ID.
    :param data: Device JSON data.
    """
    def __init__(self, server_instance=Server(), idx=None, data=None):
        self.server = server_instance
        self.idx = idx
        self.data = data
        self.values_to_update = {}

        if data is not None:
            self.idx = data["idx"]
        elif idx is not None:
            self.fetch()

    def fetch(self):
        """ Fetches device data
        """
        if self.idx is None:
            raise ValueError("Device data cannot be fetched if idx is missing")

        self.data = self.server.get_device("idx", self.idx)
        if self.data is None:
            raise ValueError("Failed to fetch device data for ID: " + str(self.idx))

    def update(self):
        """ Updates object on the server side with changed values.
        """
        if self.values_to_update is None:
            return

        # update device data on server
        self.server.update_device(self.idx, self.data["Name"], self.values_to_update)
        # fetch data from server and update current object
        self.fetch()
        # clear list
        self.values_to_update = {}

    def generic_getter(self, name, base64_decode=False):
        """ Generic properties getter.
        :param name: Name of the property.
        :param base64_decode: Whether to base64 decode,
        :return: Property value.
        :rtype: str
        """
        if self.data is None or name not in self.data:
            return

        if base64_decode:
            return base64.b64decode(self.data[name]).decode("utf-8")
        return self.data[name]

    def generic_setter(self, name, val, base64e_encode=False):
        """ Generic properties setter.
        :param name: Name of the property.
        :param base64_decode: Whether to base64 decode,
        :return: Property value.
        :rtype: str
        """
        if val is None:
            val = ""

        if base64e_encode:
            # we need to convert string to byte-like before base64 encoding
            val = base64.b64encode(val.encode()).decode("utf-8")

        if val != self.data[name]:
            self.values_to_update[name.lower()] = val

class SwitchDevice(Device):
    """ Represents Switch device.
    """
    @property
    def str_param_1(self):
        return self.generic_getter("StrParam1", True)
    @str_param_1.setter
    def str_param_1(self, val):
        self.generic_setter("StrParam1", val, True)

    @property
    def str_param_2(self):
        return self.generic_getter("StrParam2", True)
    @str_param_2.setter
    def str_param_2(self, val):
        self.generic_setter("StrParam2", val, True)

    @property
    def description(self):
        return self.generic_getter("Description")
    @description.setter
    def description(self, val):
        self.generic_setter("Description", val)

    def On(self):
        self.server.query(
            type="command",
            param="switchlight",
            idx=self.idx,
            switchcmd="On",
            level=0
        )

    def Off(self):
        self.server.query(
            type="command",
            param="switchlight",
            idx=self.idx,
            switchcmd="Off",
            level=0,
            passcode=""
        )

def device_factory(server_instance, data):
    """ Creates proper object based on device data.
    """

    if "SwitchType" in data and data["SwitchType"] == "On/Off":
        return SwitchDevice(server_instance, data=data)

    return Device(server_instance, data=data)
