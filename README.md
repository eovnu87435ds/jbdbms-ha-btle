# jbdbms-ha-btle
Janky code to read JBD/Xaiomi BMS data into home assistant over BTLE

Based on https://github.com/tgalarneau/bms with some tweaks and fixes to work for easy importing to Home Assistant.

Run this on a linux machine with bluetooth, like a raspberry pi. Needs bluepy from pip to work. 

Currently hardcoded to connect to an MQTT Server located at homeassistant.local:1883 and username homeassistant

Example:
jbdbms-ha-btle -b AA:BB:CC:11:22:33 -m jbdbms -p mqttpassword12345

You can also rename bms.sh.example to bms.sh and save your MQTT password in there. If you do that, you can also install the systemd service located in the service folder, and it will run bms.sh on boot.

By default, this updates once a minute when the reported amps are within +/- 0.2 Amps, and 10 seconds when actively dis/charging.

This script now runs forever, and sets /data/bms/availability to "online" when a BMS is connected, and "offline" when there is no BMS connected.

In the home-assistant folder is the snippet I pulled from configuration.yaml

This is hardcoded for 13s. The data responses that feed into cellvolts2 grow with each cell.
