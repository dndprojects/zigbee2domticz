return {
	active = true,
	logging = {
		level = domoticz.LOG_INFO, -- Select one of LOG_DEBUG, LOG_INFO, LOG_ERROR, LOG_FORCE to override system log level
	},
	on = {
		devices = {
			409,
		},
	},
	

	execute = function(domoticz, device)
	    mqq_host="192.168.1.3"
        mqtt_device="sonoff_zb"
        mqq_cmd="ZbSend"
        dimmer_level=device.level*10
        status =  domoticz.variables('dimmer1').value
        
	--	domoticz.log('Triggered by device: '.. device.name, domoticz.LOG_INFO)
	--	domoticz.log('Device state: @@@@@ '..device.level, domoticz.LOG_INFO)
	--	domoticz.log('Device state: @@@@@ '..device.state, domoticz.LOG_INFO)
	--	domoticz.log('Device veribale: '..status, domoticz.LOG_INFO)
	--	domoticz.log('Device lastUpdate.raw: '..dimmer_level, domoticz.LOG_INFO)
	
	    if device.state == "On" and status == "On" then
	        cmd='mosquitto_pub -h '..mqq_host..' -t cmnd/'..mqtt_device..'/'..mqq_cmd..' -m \'{ "device":"main_corridor_dimmer", "write":{"EF00/0202":'..dimmer_level..'},"Endpoint":1 }\''
		    os.execute(cmd)
--		    domoticz.log(cmd, domoticz.LOG_INFO)
	        return
	    end
	    if device.state == "Off" and status == "Off" then
	        return
	    end
		if (status == "Off") then
		    cmd='mosquitto_pub -h '..mqq_host..' -t cmnd/'..mqtt_device..'/'..mqq_cmd..' -m \'{ "device":"main_corridor_dimmer", "write":{"EF00/0101":1},"Endpoint":1 }\''
			os.execute(cmd)
	--		domoticz.log(cmd, domoticz.LOG_INFO)
			domoticz.variables('dimmer1').set("On")
		elseif 	device.state == "On" then
		    cmd='mosquitto_pub -h '..mqq_host..' -t cmnd/'..mqtt_device..'/'..mqq_cmd..' -m \'{ "device":"main_corridor_dimmer", "write":{"EF00/0202":'..dimmer_level..'},"Endpoint":1 }\''
		    os.execute(cmd)
	--	    domoticz.log(cmd, domoticz.LOG_INFO)
		end
				
		if device.state == "Off" and status == "On" then
		    cmd='mosquitto_pub -h '..mqq_host..' -t cmnd/'..mqtt_device..'/'..mqq_cmd..' -m \'{ "device":"main_corridor_dimmer", "write":{"EF00/0101":0},"Endpoint":1 }\''
		    os.execute(cmd)
	--	    domoticz.log(cmd, domoticz.LOG_INFO)
		    domoticz.variables('dimmer1').set("Off")
		end
		
	end
}


--osCommand (mosquitto_pub -h mqq_host -t cmnd..'/'..mqtt_device..'/'.. mqq_cmd '-m { "device":"0xBF13", "write":{"EF00/0101":1},"Endpoint":0 }')
--ZbSend { "device":"0x5D82", "write":{"EF00/0101":1},"Endpoint":1 }
--ZbSend { "device":"0x5D82", "write":{"EF00/0101":0},"Endpoint":1 }
--ZbSend { "device":"0x5D82", "write":{"EF00/0202":199},"Endpoint":1 }
    --    {"Device":"0x5D82","EF00/0202":320,"Endpoint":1,"LinkQuality":81}}}
 --   ZigbeeZCLSend device: 0x5D82, endpoint:1, cluster:0xEF00, cmd:0x0B, send:"0100"
