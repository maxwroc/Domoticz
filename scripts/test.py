import pprint
import domoticz

pp = pprint.PrettyPrinter(4)
server = domoticz.Server("192.168.2.103")


#pp.pprint(server.create_virtual_hardware("Heheszki"))
#pp.pprint(server.delete_hardware(name="Heheszki"))

zonk = server.get_device_obj("Name", "Master bathroom")
zonk.Off()

quit()


hr = server.get_device_obj("Name", "SmartPlug")
if isinstance(hr, domoticz.SwitchDevice):
    # script:///home/pi/maxwroc/Domoticz/scripts/hs100.sh 192.168.2.145 9999 on

    print("Prev value: " + hr.str_param_2)
    #hr.str_param_1 = "script:///home/max/git/Domoticz/scripts/hs100.sh 192.168.2.145 9999 on"
    #hr.str_param_2 = "script:///home/max/git/Domoticz/scripts/hs100.sh 192.168.2.145 9999 off"
    #hr.update()
    print("Current value: " + hr.str_param_2)
    print("Sending on/off command")
    #hr.On()
    #pp.pprint(hr.str_param_1)
else:
    print("It is not a Switch")
