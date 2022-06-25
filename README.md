# Fridge Monitor
A very simple script to monitor temperature and light state inside a refrigerator.

The code assumes one or more thermal sensors (I am using DS18B20) over a 1-wire protocol and a simple LDR/cap setup to detect the light.

Data is logged to a local server with a basic influxDB setup.

