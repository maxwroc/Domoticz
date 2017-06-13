import logging

from domoticz import (Server, Hardware)
from pyHS100 import (TPLinkSmartHomeProtocol, SmartDevice)

def install(log: logging.RootLogger, domoticz_host, domoticz_port, hardware_name):
    """ Discovers devices in the local network and installs them on Domoticz server
    """
    # log to explicit file
    logging.basicConfig(filename="installer.log", level=logging.DEBUG)

    log.info("Running installer")
    log.info("Checking domoticz server configuration")
    server = Server(domoticz_host, domoticz_port)
    log.info("  Try to get existing virtual hardware:")
    hardware = server.get_hardware_obj("Name", hardware_name)
    if hardware:
        log.info("    Found (ID:%s)", hardware.idx)
    else:
        log.info("    Not found")
        log.info("  Creating new virtual hardware:")
        hardware = Hardware(server, data=server.create_virtual_hardware(hardware_name))

        if hardware:
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

    import pprint
    pp = pprint.PrettyPrinter()
    for dev in network_devices:
        log.info(
            "  Found device: %s - %s - %s",
            dev["ip"],
            dev["sys_info"]["system"]["get_sysinfo"]["alias"],
            dev["sys_info"]["system"]["get_sysinfo"]["model"])

        smart_device = SmartDevice(dev["ip"])
        # install switch
        if not is_device_installed(installed_devices, dev, "Light/Switch"):
            log.info("    Adding virtual Switch")
            server.create_virtual_sensor(smart_device.alias, 6, hardware.idx)

        # insall usage meter
        if smart_device.has_emeter and not is_device_installed(installed_devices, dev, "Usage"):
            log.info("    Adding virtual Usage (Electric) meter")
            server.create_virtual_sensor(smart_device.alias, 16, hardware.idx)


def is_device_installed(installed_devices, device, device_type):
    chunks = []
    for i_device in installed_devices:
        if not i_device.description or i_device.type != device_type:
            return False

        chunks = i_device.description.split(":")

    return len(chunks) == 3 and chunks[1] == device["ip"]

