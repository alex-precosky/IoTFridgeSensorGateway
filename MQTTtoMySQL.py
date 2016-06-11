#!/usr/bin/env python
import paho.mqtt.client as paho
import datetime
import pymysql.cursors

tempTopicName = "/home/fridge/XBeeSensor/temperature"
batteryTopicName = "/home/fridge/XBeeSensor/batteryVoltage"

# Collect one of a temperature and a voltage then send them to the MySQL server
tempBuffer = None
voltageBuffer = None

mysql_host = "mysql.alexwarrior.cc"
mysql_user = "precosky_fridge"
mysql_passwd = "CFfFyHpZd8iTOEFSyZpy"
mysql_db = "alexwarrior_fridge"

def transmitDatapoint( temperature, voltage):


    timestamp = datetime.datetime.now()

    try:
        print("Connecting to mysql...")
        conn = pymysql.connect(host=mysql_host, user=mysql_user, passwd=mysql_passwd, db=mysql_db)
    except pymysql.err.OperationalError:
        print("Exception opening connection to mysql host")
        return

    try:
        print("INSERTing...")
        qryStr = "INSERT INTO fridge (time, temperature, batteryVoltage) VALUES (%s, %s, %s)"
        conn.cursor().execute( qryStr, (timestamp, temperature, voltage))
        print("Comitting query...")
        conn.commit()
    except pymysql.err.OperationalError:
        print("Exception transmitting datapoint to database")        
    finally:
        print("Closing connection")
        conn.close()



def on_connect(client, userdata, rc):
    print("Connected to MQTT broker")

def on_message(client, userdata, msg):
    global tempBuffer
    global voltageBuffer

    if msg.topic==tempTopicName:
        tempBuffer = float(msg.payload)
        print("Temperature received")

    elif msg.topic==batteryTopicName:
        voltageBuffer = float(msg.payload)
        print("Battery voltage received")

    if tempBuffer is not None and voltageBuffer is not None:
        print("Transmitting value %s" % datetime.datetime.now())
        transmitDatapoint( tempBuffer, voltageBuffer )
        tempBuffer = None
        voltageBuffer = None
        print("Success")


# Set up the Mqtt client and subscribe to topics
pahoClient = paho.Client()
pahoClient.on_connect = on_connect
pahoClient.on_message = on_message
pahoClient.connect("localhost", 1883, 60)
pahoClient.subscribe(tempTopicName,2)
pahoClient.subscribe(batteryTopicName,2)


pahoClient.loop_forever()
