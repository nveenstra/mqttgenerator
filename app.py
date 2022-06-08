#!/usr/bin/env python3
"""a simple sensor data generator that sends to an MQTT broker via paho"""
import sys
import json
import time
import random
import os

import paho.mqtt.client as mqtt

def generate(host, port, username, password, topic, sensors, interval_ms, verbose):
    """generate data and send it to an MQTT broker"""
    mqttc = mqtt.Client()

    if username:
        mqttc.username_pw_set(username, password)

    mqttc.connect(host, port)

    keys = list(sensors.keys())
    interval_secs = interval_ms / 1000.0

    while True:
        sensor_id = random.choice(keys)
        sensor = sensors[sensor_id]
        min_val, max_val = sensor.get("range", [0, 100])
        val = random.randint(min_val, max_val)

        data = {
            "id": sensor_id,
            "value": val
        }

        for key in ["lat", "lng", "unit", "type", "description"]:
            value = sensor.get(key)

            if value is not None:
                data[key] = value

        payload = json.dumps(data)

        if verbose:
            print("%s: %s" % (topic, payload))

        mqttc.publish(topic, payload)
        time.sleep(interval_secs)


def main():
    """main entry point, load and validate config and call generate"""
    try:
        with open("config.json") as handle:
            config = json.load(handle)
            misc_config = config.get("misc", {})
            sensors = config.get("sensors")

            interval_ms = misc_config.get("interval_ms", 500)
            verbose = misc_config.get("verbose", False)

            if not sensors:
                print("no sensors specified in config, nothing to do")
                return

            host = os.environ.get('mqtt_host')
            port = int(os.environ.get('mqtt_port'))
            username = os.environ.get('mqtt_username')
            password = os.environ.get('mqtt_password')
            topic = os.environ.get('mqtt_topic')

            print("sending data to " + host + " on port " + str(port))
            generate(host, port, username, password, topic, sensors, interval_ms, verbose)
    except OSError as error:
        print("Error connecting to host '%s'" % error)
        
# Script entry point.
if __name__ == "__main__":
    main()

