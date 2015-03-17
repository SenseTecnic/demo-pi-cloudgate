#!/usr/bin/python

# A python script that will get data from GPIO and send as a JSON event to serial

import serial
import time
import json
import sys
import Adafruit_DHT
import RPi.GPIO as GPIO, time
#import os.path
import os

# This is the device name for CloudGate, making sure we only send to this device
SERIAL_PORT = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0'
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_SENSOR_PIN = 17
LIGHT_SENSOR_PIN = 4
SHUTDOWN_PIN = 18
# Tell the GPIO library to use Broadcom GPIO references
# For light sensor
GPIO.setmode(GPIO.BCM)
# For the shutdown pin
GPIO.setup(SHUTDOWN_PIN, GPIO.IN)

ser = serial.Serial(SERIAL_PORT)

def getDHT(sensor_data):
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_SENSOR_PIN)
    sensor_data['temperature'] = '%.2f' % temperature
    sensor_data['humidity'] = '%.2f' % humidity
 
def getLight(sensor_data):
    chargeTime = RCtime(LIGHT_SENSOR_PIN)
    # transorming time in capacitor charge to light values
    light = (  chargeTime * -1 ) + 200000
    sensor_data['light'] = light
    sensor_data['value'] = light
    #TODO: wait times are too high.

# Utility function to measure analogue sensors via digital pins
# it charges a capacitor and measures the time it takes to uncharge
# giving an idea of the value in the analogue sensor.
def RCtime (PiPin):
    measurement = 0
    # Discharge capacitor
    GPIO.setup(PiPin, GPIO.OUT)
    GPIO.output(PiPin, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(PiPin, GPIO.IN)
    # Count loops until voltage across
    # capacitor reads high on GPIO
    while (GPIO.input(PiPin) == GPIO.LOW):
      measurement += 1
    return measurement

def sendData():
    while 1:

        #we will be setting value to light as it's easy to visualize
        sensor_data = {
             "temperature":"0.0",
             "humidity":"0.0",
             "light":"0",
             "value":"0"
        }

        #check for shutdown
        if(GPIO.input(SHUTDOWN_PIN)):
            print "Shutting down"
            sys.stdout.flush()    
            os.system("sudo shutdown -h now") # Send shutdown command to os
            break

        #get data
        getDHT(sensor_data)
	getLight(sensor_data)
        sensor_data_str = json.dumps(sensor_data)

        # write to serial port
        ser.write(sensor_data_str+'\n')
        time.sleep(5)
        print sensor_data_str+'\n'
        sys.stdout.flush() #when running in background flush to logs

def serial_on():
    return os.path.exists(SERIAL_PORT)    

def main():
    ison = False
    while ison is False:
        try: 
            print "Waiting for Serial..."
            sys.stdout.flush() 
            ison = serial_on()
            time.sleep(10)
        except:
            pass

    print "Sending Data on serial %s" % SERIAL_PORT
    sys.stdout.flush() 
    sendData();
    
if __name__ == "__main__":
    main()
    







