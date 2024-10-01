#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
from urllib.request import urlopen
import paho.mqtt.client as mqtt
import requests
import json
import re,time


domoticz_dict = {
    "living_room12,2": "40",
    "living_room12,1": "41",
    "living_room34,2": "42",
    "living_room34,1": "43",
    "Kids_Room,1": "66",
    "Kitchen,1": "44",
    "Pernts_Room,1": "45",
    "BathRoom,1": "46",
    "BathRoom,2": "47",
    "small_corridor,1": "50",
    "parents_bathroom,1": "51",
    "parents_bathroom,2": "53",
    "Porch,2": "77",
    "Smoke_Detector,1": "101",
    "front_door,1": "408",
    "main_corridor_dimmer,1": "409",
    "Porch,1": "410",
    "temperature_inside,1": "412",
    "temperature_outside,1": "411"
}

zigbee_power_id_dict = {
    "101" : "EF00/0401",
    "409" : "EF00/0101"
}

mqtt_server_ip = "192.168.1.3"
mqtt_server_ip_port = mqtt_server_ip + ":8080"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    mqtt_topics = ["tele/sonoff_ir/SENSOR/#", "tele/sonoff_zb/SENSOR/#"]
    #mqtt_topics = ["yicam/motion"]
    for topic in mqtt_topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    global server_msg
    server_msg = msg.payload
    global server_topic
    server_topic = str(msg.topic).replace("'", "\"")
    try: 
       result = json.loads(server_msg)
       result = "ok"
    except Exception as e:
       print(e)
       result = "bad"
    if  "SENSOR" in server_topic:
        mpayload = json.loads(server_msg,strict=False)
        #print(mpayload)
        if "ZbReceived" in mpayload:
            linkQuality=0
            try:
                device=(mpayload['ZbReceived'])
                for key in device.keys(): 
                    mydevice=key
                all=(mpayload['ZbReceived'][mydevice])
                device_name = all['Name']+","+str(all['Endpoint'])
                idx = domoticz_dict[device_name]
                power_id = 'Power'
                try:
                   if zigbee_power_id_dict[str(idx)] is not None:
                      power_id = zigbee_power_id_dict[str(idx)]
                except Exception:
                   pass
                if re.match("temperature", device_name):
                   url = "http://" + mqtt_server_ip_port + '/json.htm?type=command&param=getdevices&rid='+str(idx)
                   response = requests.get(url)
                   data = response.json()
                   temperature = str(data['result'][0]['Temp'])
                   humidity = str(data['result'][0]['Humidity'])
                   battery="100"
                   print(url)
                   try:
                       temperature=str(all['Temperature'])
                   except Exception:
                       pass
                   try:
                       humidity=str(all['Humidity'])
                   except Exception:
                       pass
                   try:
                       battery=str(all['BatteryPercentage'])
                   except Exception:
                       pass
                   mqtt_domo_publish_temperature(idx,temperature,humidity,battery)
                   return
                power_status = "unknown"
                try:
                   power_status = str(all[power_id])
                except Exception:
                   pass
                if power_status != "unknown":
                    power_status = str(all[power_id])
                    #print(device_name+":"+power_status)
                    url = "http://" + mqtt_server_ip_port + '/json.htm?type=command&param=udevice&idx=' + str(idx) + '&nvalue=' + power_status + '&svalue='  
                    data = requests.get(url).json
                    mqtt_domo_publish(idx,all,power_status)
                    #print(url)
                    #dimmner control
                    #using 2 way switch as one 
                if str(idx) == "410":
                   if check_domo_device_status(str(idx)) == "On":               
                      url = "http://" + mqtt_server_ip_port + '/json.htm?type=command&param=switchlight&idx=' + str(idx) + '&switchcmd=Off'
                      data = requests.get(url).json
                      url = "http://" + mqtt_server_ip_port + '/json.htm?type=command&param=switchlight&idx=' + str(77) + '&switchcmd=On'
                      data = requests.get(url).json
                      #print(url)
            except Exception as e:
               print("Error:")
               print(e)
                
def check_domo_device_status(idx):
    #json.htm?type=command&param=getdevices&rid=411
    url = "http://" + mqtt_server_ip_port + '/json.htm?type=command&param=getdevices&rid='+idx
    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    return (data['result'][0]['Status'])

def mqtt_domo_publish(deviceIDX,msg_json,power_status):
    topic='domoticz/in'
    #publish_data={"idx":89,"nvalue":0,"svalue":"23.9;56.1;1","Battery":100,"RSSI":9}
    linkQuality=str(msg_json['LinkQuality'])
    publish_data = {'idx':int(deviceIDX), 'nvalue':int(power_status), 'svalue':"", 'RSSI':int(int(linkQuality)/10)}
    #print(json.dumps(publish_data))
    client.publish(topic, json.dumps(publish_data))
    
def mqtt_domo_publish_temperature(deviceIDX,temperature,humidity,battery):
    #mosquitto_pub -h 192.168.1.3 -t domoticz/in  -m '{ "idx" : 411,"nvalue" : 0,"svalue" : "21;35;1"}'
    topic='domoticz/in'
    hum_status = determine_humidity_status(int(humidity))
    sval=temperature+ ";" + humidity + ";"+str(hum_status)
    publish_data = {'idx':int(deviceIDX), 'nvalue':0, 'svalue':sval, 'Battery':int(battery)}
    #print(json.dumps(publish_data))
    client.publish(topic, json.dumps(publish_data))
    
def function(json_object, name):
    for dict in json_object:
        if dict['name'] == name:
            return dict['name']
            
def update_device_status(device_dic):
    time.sleep(10)
    topic='cmnd/sonoff_zb/ZbSend'
    print("start update")
    for dict in device_dic:
        id = dict.split(",")
        print("start update - "+id[0])
        publish_data = {'Device':id[0],"read":{"Power":3}, "Endpoint":id[1]}
        client.publish(topic, json.dumps(publish_data))
        #print(topic + " " + json.dumps(publish_data))
        time.sleep(2)
        
def determine_humidity_status(humidity):
  if humidity < 30:
    hum_stat = 0
  elif 30 <= humidity < 45:
    hum_stat = 1
  elif 45 <= humidity < 70:
    hum_stat = 2
  else:
    hum_stat = 3
  return hum_stat

            
def ignore_err(json_object, name):
    try:
        do_something()
    except Exception:
         pass
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server_ip, 1883, 60)

update_thread = threading.Thread(target=update_device_status, args=(domoticz_dict,))
update_thread.start()
print("start_loop")
client.loop_forever()
