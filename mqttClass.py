
#
# Streamlined class of umqttsimple for micropython
# US Naval Academy
# Robotics and Control TSD
# Patrick McCorkell
# March 2021
#

from ubinascii import hexlify
from machine import unique_id, Timer
from umqttsimple import MQTTClient
from time import sleep
from random import randint


#USAGE:
# from mqttClass import mqttClass
#
# server = 'the broker's IP'
# mqtt = mqttClass(host_IP=server,subscriptions=YOUR_DICTIONARY_OF_SUBSCRIPTIONS)
#	  if connecting to Adafruit IO or 3rd party with username and pass:
#		   mqtt = mqttClass(host_IP=server, username='YOUR IO USER', key='YOUR IO KEY',subscriptions=YOUR_DICTIONARY_OF_SUBSCRIPTIONS)
# mqtt.connect()
# 
#
# To Subscribe:
#
# 1. Write a function with the code you want to execute when the subscription is received.
# def function_name(topic,message):
#	 ......
#	 your code for subscription
#	 ......
#
# 2. Create a dictionary['topic_name':function_name]
# Pass this dictionary at instantiation, subscriptions=YOUR_DICTIONARY_OF_SUBSCRIPTIONS)
#
#
#
# To Publish:
# mqtt.pub('topic','message')
#
#

class mqttClass:
	# Initial setup
	def __init__(self,host_IP='192.168.5.4',username=None,key=None,subscriptions=None,interval=100,timer_n=1):
		self.mqtt_server=host_IP
		# self.clientname=hexlify(unique_id()+str(randint(1000,9999)))
		self.clientname = str(randint(1000,9999))
		port=1883
		# user=b'username'
		# password=b'password'
		#mqtt=MQTTClient(clientname,mqtt_server,port,user,password)
		self.mqtt=MQTTClient(self.clientname,self.mqtt_server,port,username,key)

		self.update_timer = Timer(timer_n)
		self.timer_rate = interval

		#Array of topics currently subscribed to.
		self.topic_list=set()

		self.failcount=0

		self.mqtt.set_callback(self.callback_handler)

		topic_defaults={
			# insert topic(s) as key, and function location as value
			'test':self.test_function,
			'default':self.default_function
		}

		# Dictionary to associate subscription topics to their function()
		if type(subscriptions) is dict:
			print("registered subscription dictionary")
			self.topic_outsourcing = subscriptions
		else:
			self.topic_outsourcing = topic_defaults
	

	#Connect and maintain MQTT connection.
	def reconnect(self):
		print(self.mqtt_server+" dropped mqtt connection. Reconnecting")
		sleep(2)
		if (self.failcount<10):
			self.connect()
		else:
	  		print('Too many reconnect attempts. Restart program.')
		self.failcount+=1

	def connect(self):
		try:
			self.mqtt.connect()
			print("Connected to "+self.mqtt_server)
		except OSError as e:
			self.reconnect()
		self.failcount=0
		self.auto_subscribe()
		self.update_timer.init(mode=Timer.PERIODIC,period=self.timer_rate, callback=self.update_callback)
		return 1

	# Look for new messages on subscribed topics.
	def update_callback(self,event=None):
		try:
			self.mqtt.check_msg()
		except:
			print('ERROR: '+self.mqtt_server+' failed callback.')
			print("Quitting timer callback. Restart subscriptions.")
			self.update_timer.deinit()
			self.connect()

	def update(self):
		self.mqtt.check_msg()

	def __str__(self):
		return str(self.mqtt_server)


	#####################################################################
	####################### SUBSCRIPTION HANDLING #######################
	#####################################################################

	# Setup subscription to a topic.
	def sub(self,topic):
		self.topic_list.add(topic)
		self.mqtt.subscribe(topic)

	def auto_subscribe(self):
		# print(self.topic_outsourcing)
		for k in self.topic_outsourcing:
			self.sub(k)
			print('subscribed to ' + str(k))

	# For topic 'test', print out the topic and message
	def test_function(self,top,msg):
		print()
		print("test topic rx"+str(top))
		print(msg)
		print()

	# Redirect from MQTT callback function.
	# Error checking.
	def default_function(self,top,whatever):
		print("Discarding data: "+str(whatever)+".")
		print("No filter for topic "+str(top)+" discovered.")


	#When a message is received, this function is called.
	def callback_handler(self,bytes_topic,bytes_msg):
		# Format the data into variables that are python friendly.
		topic=bytes_topic.decode()
		message = bytes_msg.decode()
		# Locate the function for the incoming topic. If not found, use the default_function.
		topicFunction=self.topic_outsourcing.get(topic,self.default_function)
		topicFunction(topic,message)
		#return self.update()


	############################################################
	####################### PUBLISHING ##########################
	############################################################




	# Publish to a topic.
	def pub(self,topic,message):
	#	print("topic: "+topic)
	#	print("message: "+str(message))
		sent=0
		while (sent<100):
			try:
				self.mqtt.publish(topic,str(message))

	#			print("checks in the mail")
				sent=9000
			except OSError as e:
				self.mqtt.connect()
				print("mqtt dropped " + str(sent) + "times")
				sent+=1
				sleep(0.1)



