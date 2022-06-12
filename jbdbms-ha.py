#!/usr/bin/env python3
 
	# using python 3.9 
	
from bluepy.btle import Peripheral, DefaultDelegate, BTLEException
import struct
import argparse
import json
import time
import binascii
import atexit
import paho.mqtt.client as paho
 
 	# Command line arguments
parser = argparse.ArgumentParser(description='Fetches and outputs JBD bms data')
parser.add_argument("-b", "--BLEaddress", help="Device BLE Address", required=True)
#parser.add_argument("-i", "--interval", type=int, help="Data fetch interval", required=True)
parser.add_argument("-m", "--meter", help="Meter name", required=True)
parser.add_argument("-p", "--passw", help="MQTT Password")
args = parser.parse_args() 
z = 10
meter = args.meter
mqttpass = args.passw	

cells1 = []
topic ="data/bms"
gauge ="data/bms/gauge"
availability ="data/bms/availability"
broker="homeassistant.local"
port=1883

volts = -1
amps = -1
watts = -1
remain = -1
capacity = -1
cycles = -1
cell1 = -1
cell2 = -1
cell3 = -1
cell4 = -1
cell5 = -1
cell6 = -1
cell7 = -1
cell8 = -1
cell9 = -1
cell10 = -1
cell11 = -1
cell12 = -1
cell13 = -1
cell14 = -1
cell15 = -1
cell16 = -1
cellsmin = -1
cellsmax = -1
delta = -1
mincell = -1                 # identify which cell # max and min
maxcell = -1
meancell = -1

jsonpayload = {
    "meter": "bms",
    "volts": volts,
    "amps": amps,
    "watts": watts, 
    "remain": remain, 
    "capacity": capacity, 
    "cycles": cycles,
    "cell1": cell1, 
    "cell2": cell2,
    "cell3": cell3, 
    "cell4": cell4,
    "cell5": cell5, 
    "cell6": cell6, 
    "cell7": cell7, 
    "cell8": cell8,
    "cell9": cell9, 
    "cell10": cell10, 
    "cell11": cell11, 
    "cell12": cell12,
    "cell13": cell13,
    "cellsmin": cellsmin,
    "cellsmax": cellsmax,
    "delta": delta,
    "mincell": mincell,
    "maxcell": maxcell,
    "meancell": meancell
    }


def disconnect():
    mqtt.disconnect()
    print("broker disconnected")

def cellinfo1(data):			# process pack info
    infodata = data
    i = 4
    global volts
    global amps
    global watts
    global remain
    global capacity
    global cycles                        # Unpack into variables, skipping header bytes 0-3
    volts, amps, remain, capacity, cycles, mdate, balance1, balance2 = struct.unpack_from('>HhHHHHHH', infodata, i)
    volts=volts/100
    amps = amps/100
    capacity = capacity/100
    remain = remain/100
    watts = volts*amps  							# adding watts field for dbase
    
    message1 = {
        "meter": "bms",
        "volts": volts,
        "amps": amps,
        "watts": watts, 
        "remain": remain, 
        "capacity": capacity, 
        "cycles": cycles 
    }
    #print(json.dumps(message1))
    # ret = mqtt.publish(gauge, payload=json.dumps(message1), qos=0, retain=False) # not sending mdate (manufacture date)
    
    bal1 = (format(balance1, "b").zfill(16))		
    message2 = {
        "meter": "bms",							# using balance1 bits for 16 cells
        "c16" : int(bal1[0:1]), 
        "c15" : int(bal1[1:2]),                 # balance2 is for next 17-32 cells - not using
        "c14" : int(bal1[2:3]), 							
        "c13" : int(bal1[3:4]), 
        "c12" : int(bal1[4:5]), 				# bit shows (0,1) charging on-off			
        "c11" : int(bal1[5:6]), 
        "c10" : int(bal1[6:7]), 
        "c09" : int(bal1[7:8]), 
        "c08" : int(bal1[8:9]), 
        "c07" : int(bal1[9:10]), 
        "c06" : int(bal1[10:11]), 		
        "c05" : int(bal1[11:12]), 
        "c04" : int(bal1[12:13]) , 
        "c03" : int(bal1[13:14]), 
        "c02" : int(bal1[14:15]), 
        "c01" : int(bal1[15:16])
    }
    ret = mqtt.publish(topic, payload=json.dumps(message2), qos=0, retain=False)
    
def cellinfo2(data):
    infodata = data  
    i = 0                          # unpack into variables, ignore end of message byte '77'
    protect,vers,percent,fet,cells,sensors,temp1,temp2,temp3,temp4,b77 = struct.unpack_from('>HBBBBBHHHHB', infodata, i)
    temp1 = (temp1-2731)/10
    temp2 = (temp2-2731)/10			# fet 0011 = 3 both on ; 0010 = 2 disch on ; 0001 = 1 chrg on ; 0000 = 0 both off
    temp3 = (temp3-2731)/10
    temp4 = (temp4-2731)/10
    prt = (format(protect, "b").zfill(16))		# protect trigger (0,1)(off,on)
    message1 = {
        "meter": "bms",
        "ovp" : int(prt[0:1]), 			# overvoltage
        "uvp" : int(prt[1:2]), 			# undervoltage
        "bov" : int(prt[2:3]), 		# pack overvoltage
        "buv" : int(prt[3:4]),			# pack undervoltage 
        "cot" : int(prt[4:5]),		# current over temp
        "cut" : int(prt[5:6]),			# current under temp
        "dot" : int(prt[6:7]),			# discharge over temp
        "dut" : int(prt[7:8]),			# discharge under temp
        "coc" : int(prt[8:9]),		# charge over current
        "duc" : int(prt[9:10]),		# discharge under current
        "sc" : int(prt[10:11]),		# short circuit
        "ic" : int(prt[11:12]),        # ic failure
        "cnf" : int(prt[12:13])	    # config problem
    }
    # ret = mqtt.publish(topic, payload=json.dumps(message1), qos=0, retain=False)
    
    message2 = {
        "meter": "bms",
        "protect": protect,
        "percent": percent,
        "fet": fet,
        "cells": cells,
        "temp1": temp1,
        "temp2": temp2,
        "temp3": temp3,
        "temp4": temp4
    }
    # ret = mqtt.publish(topic, payload=json.dumps(message2), qos=0, retain=False)    # not sending version number or number of temp sensors

def cellvolts1(data):			# process cell voltages
    global cells1
    celldata = data             # Unpack into variables, skipping header bytes 0-3
    i = 4
    global cell1
    global cell2
    global cell3
    global cell4
    global cell5
    global cell6
    global cell7
    global cell8
    cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8 = struct.unpack_from('>HHHHHHHH', celldata, i)
    cell1 = cell1/1000
    cell2 = cell2/1000
    cell3 = cell3/1000
    cell4 = cell4/1000
    cell5 = cell7/1000
    cell6 = cell6/1000
    cell7 = cell7/1000
    cell8 = cell8/1000
    cells1 = [cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8] 	# needed for max, min, delta calculations

    # message = {
    #     "meter" : "bms", 
    #     "cell1": cell1, 
    #     "cell2": cell2,
    #     "cell3": cell3, 
    #     "cell4": cell4,
    #     "cell5": cell5, 
    #     "cell6": cell6, 
    #     "cell7": cell7, 
    #     "cell8": cell8 
    # }
    # ret = mqtt.publish(gauge, payload=json.dumps(message), qos=0, retain=False)
   
def cellvolts2(data):			# process cell voltages
    celldata = data
    i = 0                       # Unpack into variables, ignore end of message byte '77'
    global cell9
    global cell10
    global cell11
    global cell12
    global cell13
    global cellsmin
    global cellsmax
    global delta
    global mincell                # identify which cell # max and min
    global maxcell
    global meancell
    cell9, cell10, cell11, cell12, cell13, cell14, b77 = struct.unpack_from('>HHHHHHB', celldata, i)
    cell9 = cell9/1000
    cell10 = cell10/1000
    cell11 = cell11/1000
    cell12 = cell12/1000
    cell13 = cell13/1000
    # message = {
	#     "meter": "bms", 
    #     "cell9": cell9, 
    #     "cell10": cell10, 
    #     "cell11": cell11, 
    #     "cell12": cell12,
    #     "cell13": cell13, 
    # }
    # print(message)
    # ret = mqtt.publish(gauge, payload=json.dumps(message), qos=0, retain=False)
    
    cells2 = [cell9, cell10, cell11, cell12, cell13]	# adding cells min, max and delta values	
    allcells = cells1 + cells2
    cellsmin = min(allcells)
    cellsmax = max(allcells)
    delta = round((cellsmax-cellsmin),3)
    mincell = (allcells.index(min(allcells))+1)                 # identify which cell # max and min
    maxcell = (allcells.index(max(allcells))+1)
    meancell = round((sum(allcells) / len(allcells)), 3)
    # message1 = {
    #     "meter": meter,
    #     "mincell": mincell,
    #     "cellsmin": cellsmin,
    #     "maxcell": maxcell,
    #     "cellsmax": cellsmax,
    #     "delta": delta
    # }
    # ret = mqtt.publish(gauge, payload=json.dumps(message1), qos=0, retain=False)
    
class MyDelegate(DefaultDelegate):		# handles notification responses
	def __init__(self):
		DefaultDelegate.__init__(self)
	def handleNotification(self, cHandle, data):
		hex_data = binascii.hexlify(data) 		# Given raw bytes, get an ASCII string representing the hex values
		text_string = hex_data.decode('utf-8')
		print(text_string)
		if text_string.find('dd04') != -1:		# check incoming data for routing to decoding routines
			cellvolts1(data)
		elif text_string.find('dd03') != -1:
			cellinfo1(data)
		elif text_string.find('77') != -1 and len(text_string) == 26:	 # x04
			cellvolts2(data)
		#elif text_string.find('77') != -1 and len(text_string) == 28:	 # x03
			#cellinfo2(data)	
atexit.register(disconnect)
mqtt = paho.Client("control3")      #create and connect mqtt client
mqtt.username_pw_set("homeassistant", mqttpass)
mqtt.connect(broker,port)     


		# write empty data to 0x15 for notification request   --  address x03 handle for info & x04 handle for cell voltage
		# using waitForNotifications(5) as less than 5 seconds has caused some missed notifications
while True:
    try:
        print('attempting to connect')		                # connect bluetooth device
        mqtt.publish(availability, "offline", qos=0, retain=True)
        bms = Peripheral(args.BLEaddress,addrType="public")
    except BTLEException as ex:
        continue
        #time.sleep(10)
        #print('2nd try connect')
        #bms = Peripheral(args.BLEaddress,addrType="public")
    #except BTLEException as ex:
    #    print('cannot connect')
    #    exit()
    else:
        print('connected ',args.BLEaddress)

    # atexit.register(disconnect)
    # mqtt = paho.Client("control3")      #create and connect mqtt client
    # mqtt.username_pw_set("homeassistant", mqttpass)
    # mqtt.connect(broker,port)     
    bms.setDelegate(MyDelegate())		# setup bt delegate for notifications

    # 		# write empty data to 0x15 for notification request   --  address x03 handle for info & x04 handle for cell voltage
    # 		# using waitForNotifications(5) as less than 5 seconds has caused some missed notifications
    while True:
        try:
            result = bms.writeCharacteristic(0x15,b'\xdd\xa5\x04\x00\xff\xfc\x77',False)		# write x04 w/o response cell voltages
            bms.waitForNotifications(5)
        except:
            break
        
        try:
            result = bms.writeCharacteristic(0x15,b'\xdd\xa5\x03\x00\xff\xfd\x77',False)		# write x03 w/o response cell info
            bms.waitForNotifications(5)
        except:
            break
        jsonpayload = {
            "meter": "bms",
            "volts": volts,
            "amps": amps,
            "watts": watts, 
            "remain": remain, 
            "capacity": capacity, 
            "cycles": cycles,
            "cell1": cell1, 
            "cell2": cell2,
            "cell3": cell3, 
            "cell4": cell4,
            "cell5": cell5, 
            "cell6": cell6, 
            "cell7": cell7, 
            "cell8": cell8,
            "cell9": cell9, 
            "cell10": cell10, 
            "cell11": cell11, 
            "cell12": cell12,
            "cell13": cell13,
            "cellsmin": cellsmin,
            "cellsmax": cellsmax,
            "delta": delta,
            "mincell": mincell,
            "maxcell": maxcell,
            "meancell": meancell
            }
        mqtt.publish(gauge, payload=json.dumps(jsonpayload), qos=0, retain=False)
        mqtt.publish(availability, "online", qos=0, retain=True)
        if amps >= 0.2 or amps <= -0.2:
            z = 10
        else:
            z = 60
        time.sleep(z)
