#!/usr/bin/python

# A python script that will get data from GPIO and send as a JSON event to serial

import serial
import time
import json
import sys
import Adafruit_DHT
import RPi.GPIO as GPIO, time
import os
import threading
from Queue import Queue

# This is the device name for CloudGate, making sure we only send to this device
SERIAL_PORT = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0'
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_SENSOR_PIN = 17
LIGHT_SENSOR_PIN = 4
LED_ACTUATOR_PIN = 24
SHUTDOWN_PIN = 18
# Tell the GPIO library to use Broadcom GPIO references
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTDOWN_PIN, GPIO.IN)
GPIO.setup(LED_ACTUATOR_PIN, GPIO.OUT)

#SETUP SERIAL
ser = serial.Serial(SERIAL_PORT)
ser.timeout = 10;

#THREAD AND QUEUE SETUP
serial_in_queue = Queue(maxsize=0)
serial_out_queue = Queue(maxsize=0)
num_threads = 10

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

# A thread to wrap up serial writes and reads.
# class is json agnostic, so data should be formatted before being put into:
# serial_in_queue and serial_out_queue
class serialThread (threading.Thread):
    def __init__(self, serial_port):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(serial_port)

    def run(self):
        while True:
            
            line_in = self.ser.readline()
            if line_in:
                serial_in_queue.put(line_in)

            line_out = serial_out_queue.get()        
            if line_out:
                self.ser.write(line_out)
            serial_out_queue.task_done()

class actuatorsThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            line = serial_in_queue.get()
            serial_in_queue.task_done()
            if line:
                data = json.loads(line)
                if data:
                    for event in data:
                        try:
                            button = data[0]['button']                                       
                            if button == 'on':
                                GPIO.output(LED_ACTUATOR_PIN,True)
                            if button == 'off':
                                GPIO.output(LED_ACTUATOR_PIN,False)
                        except KeyError: #if another control is sent (e.g. slider)
                            "Do Nothing"

class sensorsThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #we will be setting value to light as it's easy to visualize
        self.sensor_data = {
             "temperature":"0.0",
             "humidity":"0.0",
             "light":"0",
             "value":"0"
        }

    def run(self):
        while True:

            #check for shutdown
            if(GPIO.input(SHUTDOWN_PIN)):
                print "Shutting down"
                sys.stdout.flush()    
                os.system("sudo shutdown -h now") # Send shutdown command to os
                break

            #get sensor data
            getDHT(self.sensor_data)
    	    getLight(self.sensor_data)
            sensor_data_str = json.dumps(self.sensor_data)
            serial_out_queue.put(sensor_data_str+'\n')

            time.sleep(3)

def serial_on():
    return os.path.exists(SERIAL_PORT)    

def main():
    ison = False
    while ison is False:
        try: 
            print "Waiting for Serial..."
            sys.stdout.flush() 
            ison = serial_on()
            time.sleep(5)
        except:
            pass

    print "Using serial %s" % SERIAL_PORT
    sys.stdout.flush() 

    serial_thread = serialThread(SERIAL_PORT)
    serial_thread.start()

    sensors_thread = sensorsThread()
    sensors_thread.start()

    actuators_thread = actuatorsThread()
    actuators_thread.start()

    serial_in_queue.join()
    serial_out_queue.join()
    
if __name__ == "__main__":
    main()
    







