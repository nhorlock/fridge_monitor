#!/usr/bin/python3
import argparse
import time
import sys
import datetime
import json
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError
import logging

from gpiozero import LightSensor
from w1thermsensor import W1ThermSensor
from time import sleep

measurement = "fridge"
fridge_light_on = True

def send_data_to_influx(store, row):
    try:
        store.write_points(row, time_precision='s')
    except ConnectionError as e:
        logging.warning("Failed to connect to Influx host {}:{} - {}".format(dbhost, port, e))
    except InfluxDBClientError as e:
        if e.code == 404:
            logging.error("Database '{}' not found.".format(dbname))
        else:
            logging.error("Write InfluxDB client failed {}@{}:{} - {}".format(dbname,dbhost, port, e))
    except InfluxDBServerError as e:
            logging.error("Write InfluxDB server failed {}@{}:{} - {}".format(dbname,dbhost, port, e))


def light_on():
	global fridge_light_on
	fridge_light_on = True
	read_therm()

def light_off():
	global fridge_light_on
	fridge_light_on = False
	read_therm()

def read_therm():
	readings = {}
	readings["light"] = fridge_light_on
	for sensor in W1ThermSensor.get_available_sensors():
		readings["temp_"+sensor.id] = sensor.get_temperature()

	row = [ { "measurement":measurement,
				"tags": {},
				"time": int(time.time()),
				"fields":readings
			}
		]
	logging.debug(json.dumps(row))
	send_data_to_influx(store, row)
# Allow setting of basic config at commandline.

parser = argparse.ArgumentParser(description='Generating report cards for STAC-M3 Streaming™')
parser.add_argument('--dbhost', dest='dbhost', required=False, default="babbage.local",
                    help="The IP or resolvable hostname of the influx data base")
parser.add_argument('--dbport', dest='port', required=False, default=8086, 
                    help="The port number for the influx data base")
parser.add_argument("--user", dest='user', required=False, default="fridgemon",
                    help="the influx username")
parser.add_argument("--pass", dest='pw', required=False, default="fridgemon",
                    help="the influx password")
parser.add_argument("--dbname", dest='dbname', required=False, default="fridgemon",
                    help="the influx database that will be used.")
args = parser.parse_args()

dbhost = args.dbhost
port   = args.port
user   = args.user
pw     = args.pw
dbname = args.dbname

# Create the InfluxDB client object
store = InfluxDBClient(dbhost, port, user, pw, dbname)

ldr = LightSensor(23, queue_len=1)
ldr.when_light = light_on
ldr.when_dark = light_off

while True:
	read_therm()
	sleep(5)
