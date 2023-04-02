import json
import logging
import threading
import time
from configparser import ConfigParser
import requests
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO)

config = ConfigParser()
config.read("config.ini")

broker = config.get("MQTT", "MQTTBroker")
port = config.getint("MQTT", "port")
client_id = config.get("MQTT", "client_id_pub")
mqtt_user = config.get("MQTT", "mqtt_user")
mqtt_password = config.get("MQTT", "mqtt_password")

system_url = config.get("URL", "system_url")
docker_url = config.get("URL", "docker_url")

sendAsMQTT = config.getboolean("MQTT", "sendAsMQTT")
sendSystem = config.getboolean("MQTT", "sendSystem")
sendDocker = config.getboolean("MQTT", "sendDocker")

# Topic configuration
topic1 = config.get("Topic", "topic1")
topic2 = config.get("Topic", "topic2")
topic3 = config.get("Topic", "topic3")

client = mqtt.Client(client_id)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
        client.subscribe(topic1)
    else:
        logging.error("Failed to connect, return code %d\n", rc)


def on_disconnect(client, userdata, rc):
    logging.warning("Disconnected with result code %d", rc)
    client.subscribe(topic1)


def on_publish(client, userdata, mid):
    logging.info("Published message with id %d", mid)


def connect_mqtt():
    try:
        client.username_pw_set(mqtt_user, mqtt_password)
        client.connect(broker, port)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        return client
    except Exception as e:
        logging.error("Error connecting to MQTT broker: %s", e)
        return None


def fetch_data(url):
    try:
        with requests.get(url) as response:
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logging.error("Error fetching data: %s", e)
        return None


def format_data(data):
    if data is None:
        return None
    else:
        return ",".join("{}={}".format(*i) for i in data.items()).replace(
            "{}", " "
        ).replace("{", " ").replace("}", " ").replace(" , ", " ")


def publish(client):
    message_count = 0
    ses = requests.session()
    while True:
        req = ses.get(system_url)
        data = req.json()
        time.sleep(1)

        res = ",".join("{}={}".format(*i) for i in data.items()).replace('{}', ' ').replace('{', ' ').replace('}',
                                                                                                              ' ').replace(
            " , ", ' ')

        if sendAsMQTT:
            if sendDocker:
                result = client.publish(topic1, res)
                topic = topic1
            elif sendSystem:
                result = client.publish(topic2, res)
                topic = topic2
            else:
                result = client.publish(topic3, res)
                topic = topic3

            status = result[0]
            if status == 0:
                print("Sent '{message}' to topic '{topic}' via MQTT".format(message=res, topic=topic))
            else:
                print("Failed to send message to topic '{topic}' via MQTT".format(topic=topic))
        else:
            if sendDocker:
                url = docker_url
            else:
                url = system_url

            headers = {
                'Content-Type': 'application/json'
            }
            data = json.dumps(data)
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                print("Sent data to '{url}' via HTTP".format(url=url))
            else:
                print("Failed to send data to '{url}' via HTTP".format(url=url))

        message_count += 1
        time.sleep(1)


def publish_job():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.disconnect()
    client.loop_stop()
