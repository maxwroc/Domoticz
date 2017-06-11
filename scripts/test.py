import pprint
import domoticz

pp = pprint.PrettyPrinter(4)
server = domoticz.Server("192.168.2.104")


#pp.pprint(server.createVirtualHardware("Heheszki"))
pp.pprint(server.deleteHardware(id = 6))