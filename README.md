======================
Pi-to-Cloudgate-Sensor
======================

This is an example python script that reads sensor data from a Raspberry Pi's GpIO and prints it to serial as a JSON object. By default this script is to be used with a CloudGate and is configured to print to the following serial port:

```
/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0
```

Dependencies
================

This assumes you are using raspbian 
* Raspbian OS running in your Raspberry Pi.
* Python >2.7 (sudo apt-get install python-dev)
* Adafruit's DHT-sensor-library (https://github.com/adafruit/DHT-sensor-library)
* RPi modules (sudo apt-get install python-rpi.gpio)

Wiring up the Raspbery Pi
=========================

This script takes input from:

* Pin 17: A DHT11 humidity and temperature sensor
* Pin 4: A light sensor (photoresistor)
* Pin 18: A button to be used to poweroff the Pi safely.

The pi can be wired like this: 

![alt tag](https://raw.github.com/sensetecnic/{projectname}/master/sensor-setup.jpg)

Running the script
==================

You can run the script using:

```
sudo python wotkitdemo.py
```

Running at boot
===============

We provide a bash script named ``runwotkitdemo.sh'' you can use to deploy at boot. First create a log file named 'cronlog', in our case we have created it at ```/home/pi/wotkitdemo/logs```. 

Then you can add the following line to your crontab via ```sudo crontab -e```, which will boot the

```
@reboot sudo sh /home/pi/wotkitdemo/runwotkitdemo.sh > /home/pi/wotkitdemo/logs/cronlog 2>&1 &
```

