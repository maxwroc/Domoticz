import pprint
import domoticz

pp = pprint.PrettyPrinter(4)
server = domoticz.Server("192.168.2.104")


#pp.pprint(server.create_virtual_hardware("Heheszki"))
pp.pprint(server.delete_hardware(name="Heheszki"))
