import logging

from domoticz import (Server, Hardware, Device)
from pyHS100 import (TPLinkSmartHomeProtocol, SmartDevice)

def install(log: logging.RootLogger, domoticz_host, domoticz_port, hardware_name):
    """ Discovers devices in the local network and installs them on Domoticz server
    """
    # log to explicit file
    logging.basicConfig(filename="installer.log", level=logging.DEBUG)

    log.info("Running installer")
    log.info("Checking Domoticz server configuration")
    server = Server(domoticz_host, domoticz_port)
    log.info("  Try to get existing virtual hardware")
    hardware = server.get_hardware_obj("Name", hardware_name)
    if hardware:
        log.info("    Found (ID:%s)", hardware.idx)
    else:
        log.info("    Not found")
        log.info("  Creating new virtual hardware")
        hardware = Hardware(server, data=server.create_virtual_hardware(hardware_name))

        if hardware and hardware.idx:
            log.info("    Created")
        else:
            log.info("    Failed")
            return

    log.info("  Getting installed devices")
    installed_devices = hardware.get_devices()
    if installed_devices:
        for device in installed_devices:
            log.info(
                "    Found device: %s (%s) %s",
                device.idx, device.data["Type"], device.data["Description"])
    else:
        log.info("    Devices not found")

    print("Discovering devices in your local network...")
    network_devices = TPLinkSmartHomeProtocol.discover()

    for dev in network_devices:
        log.info(
            "  Found device: %s - %s - %s",
            dev["ip"],
            dev["sys_info"]["system"]["get_sysinfo"]["alias"],
            dev["sys_info"]["system"]["get_sysinfo"]["model"])

        smart_device = SmartDevice(dev["ip"])
        # install switch
        description = "%s:%s:%s" % (smart_device.alias, smart_device.ip_address, dev["port"])
        if is_device_installed(installed_devices, dev, "Light/Switch"):
            log.info("    Virtual Switch installed on Domoticz already")
        else:
            log.info("    Adding virtual Switch on Domoticz")
            create_sensor(server, smart_device.alias, 6, description, hardware.idx)

        # insall usage meter
        if smart_device.has_emeter:
            if is_device_installed(installed_devices, dev, "Usage"):
                log.info("    Virtual Usage (Electric meter) installed already")
            else:
                log.info("    Adding virtual Usage (Electric) meter on Domoticz")
                create_sensor(server, smart_device.alias, 248, description, hardware.idx)

def create_sensor(server, device_name, device_type, description, hardware_id):
    device_data = server.create_virtual_sensor(device_name, device_type, int(hardware_id))
    if not device_data:
        raise ValueError("Missing new device data")

    new_device = Device(server, data=device_data)
    new_device.description = description
    new_device.update()

def is_device_installed(installed_devices, device, device_type):
    for i_device in installed_devices:
        assert isinstance(i_device, Device)
        if i_device.description and i_device.type_string == device_type:
            chunks = i_device.description.split(":")
            if len(chunks) == 3 and chunks[1] == device["ip"]:
                return True

    return False

