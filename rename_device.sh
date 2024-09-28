#!/bin/bash

curl -s -H "Accept: application/json" -X GET 'http://192.168.1.3:8080/json.htm?type=command&param=getdevices&used=true&displayhidden=1' | grep Zigbee | tr "," " " | sed "s#"\""##g" | awk '{print "\""$(NF)","$(NF-2)"\": \""$(NF-1)"\","}' > /tmp/zigbee_list.txt

curl -s -H "Accept: application/json" -X GET 'http://192.168.1.3:8080/json.htm?type=command&param=getdevices&used=true&displayhidden=1' | grep Zigbee | tr "," " " | sed "s#"\""##g" | awk '{print  "mosquitto_pub -h 192.168.1.3 -t cmnd/sonoff_zb/ZbName -m __"$(NF-3)","$(NF)"__"}' | sed "s#__#'#g" > /tmp/zigbee_list.csh

#source /tmp/zigbee_list.csh
cat /tmp/zigbee_list.txt

#rm /tmp/zigbee_list.csh
#rm /tmp/zigbee_list.txt
