import OPi.GPIO as RPIO
import threading

class CardReader(object):
	"""Class representing a reader. One object should be instantiated for each physical reader"""

	def __init__(self, name, GPIO_0, GPIO_1, TIMEOUT):
		#Pins used to receive 0s and 1s
		self.name = name
		self.GPIO_0 = GPIO_0
		self.GPIO_1 = GPIO_1
	
		self.tag = "" #The buffer used to store the RFID Tag
		self.TIMEOUT = TIMEOUT #Real time allowed for the transmission
		super().__init__()

	def addBitToTag(self, gpio_id):
		#Beginning of a new frame, we start the timer
		if self.tag == "":
			self.t = threading.Timer(self.TIMEOUT, self.processTag)
			self.t.start()

		#We check wether we received a 0 or a 1
		if gpio_id == self.GPIO_0:
			self.tag += "0"
		elif gpio_id == self.GPIO_1:
			self.tag += "1"	

	def registerReader(self, edge = RPIO.FALLING, pull_up_down=RPIO.PUD_UP):
		RPIO.setup(self.GPIO_0, pull_up_down)
		RPIO.setup(self.GPIO_1, pull_up_down)
		RPIO.add_event_detect(self.GPIO_0, edge, callback=self.addBitToTag)
		RPIO.add_event_detect(self.GPIO_1, edge, callback=self.addBitToTag)
		 
		#Initializing timer
		self.t = threading.Timer(0.1, self.processTag)
		self.t.start()

	def removeReader(self):
		RPIO.remove_event_detect(self.GPIO_0)
		RPIO.remove_event_detect(self.GPIO_1)

	#Method triggered after Timer tick that prints out the tag
	def processTag(self):
		if self.tag == "":
			return
		elif len(self.tag) < 10:
			print("[" + self.name + "] Frame of length (" + str(len(self.tag)) + "):" + self.tag + " DROPPED")
		elif self.verifyParity(self.tag):
			print("[" + self.name + "] Frame of length (" + str(len(self.tag)) + "): " + self.tag + " (" + str(CardReader.binaryToInt(self.tag)) + ") OK KOI" )
		
		self.tag = ""

	def verifyParity(self, binary_string):
		first_part = binary_string[0:13]
		second_part = binary_string[13:]
		parts = [first_part, second_part]
		bitsTo1 = [0, 0]
		index = 0		

		for part in parts:
			bitsTo1[index] = part.count('1')
			index += 1

		if bitsTo1[0] % 2 != 0 or bitsTo1[1] % 2 != 1:
			print("[" + self.name + "] Frame of length (" + str(len(self.tag)) + "): " + self.tag + " (" + str(CardReader.binaryToInt(self.tag)) + ") - PARITY CHECK FAILED")
			return False
		return True

	#Method to convert the RFID binary value into a readable integer
	@staticmethod
	def binaryToInt(binary_string):
		print(binary_string)
		binary_string = binary_string[1:-1] #Removing the first and last bit (Non-data bits)
		print(binary_string)
		result = int(binary_string, 2)
		return result