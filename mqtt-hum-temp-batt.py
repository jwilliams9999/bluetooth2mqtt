#!/usr/bin/env python3
import datetime
import time
from time import sleep
from bleson import get_provider, Observer
import paho.mqtt.client as mqtt
timeout = time.time() + 30*1
last = {}

def temp_hum(values):
    values = int.from_bytes(values, 'big')
    is_negative = values & 0x800000 != 0
    if is_negative:
       values = values ^ 0x800000
    humidity = (values % 1000) / 10
    temp = int(values / 1000) / 10

    if is_negative:
       temp = 0 - temp

    if temp < 110:
       temp = temp * 9 / 5 + 32
    else:
       temp = None

    return round(temp,1),round(humidity,1)


def on_advertisement(advertisement):
    mac_addr = str(advertisement.address)[11:-2]
    MQTT_BROKER_URL    = "10.1.1.151"

    mac_dict = {'A4:C1:38:B9:21:7A' : ['temperature/LakeHouse/kitchen','humidity/LakeHouse/kitchen',\
                'battery/LakeHouse/kitchen'],\
                'A4:C1:38:80:89:3C' : ['temperature/LakeHouse/tvroom','humidity/LakeHouse/tvroom',\
                'battery/LakeHouse/tvroom'],\
                'A4:C1:38:77:99:84' : ['temperature/LakeHouse/bath','humidity/LakeHouse/bath',\
                'battery/LakeHouse/bath']}

    if mac_addr in mac_dict:
      mfg_data = advertisement.mfg_data
      temp=temp_hum(mfg_data[3:6])
      batt = mfg_data[6]
      MQTT_TOPIC_TEMP = mac_dict[mac_addr][0]
      MQTT_TOPIC_HUM = mac_dict[mac_addr][1]
      MQTT_TOPIC_BATT = mac_dict[mac_addr][2]
    else:
      return

    mqttc = mqtt.Client()
    mqttc.connect(MQTT_BROKER_URL)
    mqttc.publish(MQTT_TOPIC_TEMP, temp[0])
    mqttc.publish(MQTT_TOPIC_HUM,temp[1])
    mqttc.publish(MQTT_TOPIC_BATT,batt)
    print(f"Published new temperature measurement: {mac_addr} {temp[0]}F Humidity: {temp[1]} battery: {batt}%")

adapter = get_provider().get_adapter()

observer = Observer(adapter)
observer.on_advertising_data = on_advertisement

observer.start()
while True:
    sleep(1)
    if time.time() > timeout:
       break
observer.stop()
