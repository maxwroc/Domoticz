import logging

from domoticz import Server
from pyHS100 import TPLinkSmartHomeProtocol

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
        hardware = server.create_virtual_hardware(hardware_name)
        if hardware:
            log.info("    Created")
        else:
            log.info("    Failed")
            return

    log.info("  Getting installed devices")
    devices = hardware.get_devices()
    if devices:
        for device in devices:
            log.info(
                "    Found device: %s (%s) %s",
                device.idx, device.data["Type"], device.data["Description"])
    else:
        log.info("    Devices not found")

    print("Discovering devices in your local network...")
    network_devices = TPLinkSmartHomeProtocol.discover()
    for dev in network_devices:
        log.info(
            "  Found device: %s (%s)",
            dev["ip"],
            dev["sys_info"]["system"]["get_sysinfo"]["alias"])
