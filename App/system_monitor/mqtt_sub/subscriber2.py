import configparser
import json
import logging

from flask_apscheduler import scheduler
from paho.mqtt import client as mqtt_client

logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
config.read("config.ini")

broker = config.get("MQTT", "MQTTBroker")
port = config.getint("MQTT", "port")
client_id = config.get("MQTT", "client_id_sub")

# Topic configuration
topic1 = config.get("Topic", "topic1")
topic2 = config.get("Topic", "topic2")
topic3 = config.get("Topic", "topic3")


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
            client.subscribe([(topic1, 1), (topic2, 1), (topic3, 1)])
        else:
            logging.error("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def on_message(client, userdata, message):
    try:
        print("Received `{payload}` from `{topic}` topic".format(payload=message.payload.decode(), topic=message.topic))
    except Exception as e:
        print("Error in on_message:" + str(e))


def subscribe_job():
    mqtt_client = connect_mqtt()
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()
