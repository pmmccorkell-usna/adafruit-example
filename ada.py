#
# Streamlined class of umqttsimple for micropython
# US Naval Academy
# Robotics and Control TSD
# Patrick McCorkell
# May 2021
#

from machine import Pin
from time import sleep
from mqttClass import mqttClass
import OLED

########## IMPORTANT READ ###########
# ENTER the following in user_data.py
# ada_user='your adafruit io username'
# ada_key='your adafruit io API key'
from user_data import *

led_pin = Pin(25,Pin.OUT)
led_pin.value(0)

def led_function(topic,msg):
	if (msg=='ON'):
		led_pin.value(1)
		print('led on')
		OLED.ip('LED on')
	else:
		led_pin.value(0)
		print('led off')
		OLED.ip('LED off')

def logo_function(topic,msg):
	if (int(msg)==1):
		print('logo image')
		OLED.WRCE2()

def name_function(topic,msg):
	print('name: '+str(msg))
	OLED.nametag(str(msg))

def tea_function(topic,msg):
	if (int(msg)==1):
		print('tea image')
		OLED.yoda()

def value_function(topic,msg):
	print('rx: '+str(msg))
	OLED.ip('rx: '+str(msg))

sub_dict = {
	'wrcetsd/feeds/led' : led_function,
	'wrcetsd/feeds/logo' : logo_function,
	'wrcetsd/feeds/name' : name_function,
	'wrcetsd/feeds/tea' : tea_function,
	'wrcetsd/feeds/value' : value_function
}


ada_server = 'io.adafruit.com'

mqtt = mqttClass(host_IP=ada_server,username=ada_user,key=ada_key,subscriptions=sub_dict)
mqtt.connect()
