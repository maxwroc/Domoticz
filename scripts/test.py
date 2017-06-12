import pprint
import domoticz

pp = pprint.PrettyPrinter(4)
server = domoticz.Server("192.168.2.104")


#pp.pprint(server.create_virtual_hardware("Heheszki"))
#pp.pprint(server.delete_hardware(name="Heheszki"))

hr = server.get_device_obj("idx", 176)
if isinstance(hr, domoticz.SwitchDevice):
    # script:///home/pi/maxwroc/Domoticz/scripts/hs100.sh 192.168.2.145 9999 on

    print("Prev value: " + hr.str_param_1)
    hr.str_param_1 = "script:///home/pi/maxwroc/Domoticz/scripts/hs100.sh 192.168.2.145 9999 on kukuryku"
    hr.update()
    print("Current value: " + hr.str_param_1)
    #pp.pprint(hr.str_param_1)
else:
    print("It is not a Switch")
