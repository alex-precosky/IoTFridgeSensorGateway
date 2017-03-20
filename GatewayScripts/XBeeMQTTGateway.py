#!/usr/bin/env python

# For python 3
# Needs the XBee package https://pypi.python.org/pypi/XBee

import sys
import datetime
from xbee import XBee
import urllib
import urllib.request

import optparse
parser = optparse.OptionParser()

import serial
import re
import http.client

import paho.mqtt.client as paho

# Listens on the serial port for packets from the XBee fridge sensor, and publishes them
# to an MQTT broker

serialportname = '/dev/ttyUSB0'


pahoClient = paho.Client()
tempTopicName = "/home/fridge/XBeeSensor/temperature"
batteryTopicName = "/home/fridge/XBeeSensor/batteryVoltage"


def logPoint( tempValue, batVoltageValue, no_send ):
    data = {}
    data['temp']=tempValue
    data['batvoltage']=batVoltageValue
	
    print("Publishing to MQTT server")
    (mqttResult, mid) = pahoClient.publish(tempTopicName, tempValue, retain=True)
    if mqttResult == paho.MQTT_ERR_NO_CONN:
        print("Error: No MQTT connection")

    (mqttResult, mid) = pahoClient.publish(batteryTopicName, batVoltageValue, retain=True)    
    print("MQTT publish complete")
    print("\n")



def main():
   
    ser = serial.Serial(serialportname, 57600)
    xbee = XBee(ser)

    parser.add_option('--no-send', action="store_true", 
                    default=False, 
                    dest="no_send",
                  help="Don't transmit anything",
                  )
	
    (options, args) = parser.parse_args()
	
    pahoClient.connect("localhost", 1883, 60)
    pahoClient.loop_start()
    

    while True:

        try:
            response = xbee.wait_read_frame()

            print("XBee packet received")
            print("Time: %s RSSI: -%d dBm" % (datetime.datetime.now().isoformat(), ord(response['rssi'])))
            print(response['rf_data'])

            m = re.search('(?<=values=).[\d\.,]+', str(response['rf_data']))
            if m:
                values = m.group(0).split(',',2)

                tempValue = values[0]
                batVoltageValue = values[1]

                logPoint(tempValue, batVoltageValue, options.no_send)

        except KeyboardInterrupt:
            break

    ser.close()

    
if __name__ == '__main__':
    main()
