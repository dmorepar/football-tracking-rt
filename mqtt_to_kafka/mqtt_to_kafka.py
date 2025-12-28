import json
from paho.mqtt import client as mqtt_client
from confluent_kafka import Producer

# -------- CONFIG --------
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'football/players'

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'players_topic'

# -------- Kafka Producer --------
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    # else:
    #     print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# -------- MQTT Callback --------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect to MQTT, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"MQTT -> Kafka: {payload}")
    producer.produce(KAFKA_TOPIC, payload.encode('utf-8'), callback=delivery_report)
    producer.flush()

# -------- MQTT Client --------
client = mqtt_client.Client(client_id="mqtt_to_kafka_bridge")
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()
