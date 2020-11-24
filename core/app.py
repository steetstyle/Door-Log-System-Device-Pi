import sys
import os
sys.path.append(os.getcwd())
from time import sleep
from pyA20.gpio import gpio
from pyA20.gpio import port
import threading

class App:

    continue_reading = False
    name = ""
    tag = ""
    BIT_TRANSMISSION_TIME = 0.002 #From wiegand specification
    FRAMESIZE = 48 #Supposed size of received frame
    FRAMETIME = FRAMESIZE * BIT_TRANSMISSION_TIME #Theoric time necessary to transfer a frame
    ALLOWANCE = 10 #Auhtorized allowance for the transmission time in percent
    TIMEOUT = FRAMETIME*(1+ALLOWANCE/100) #Real time allowed for the transmission
    
    def __init__(self):
        self.setup()

    def setup(self):
        gpio.init()

        self.GPIO_0 = port.PB11
        self.GPIO_1 = port.PB11
        self.name = "Okuyucu 1 : "
        gpio.setcfg(self.GPIO_0,gpio.INPUT)
        gpio.setcfg(self.GPIO_1, gpio.INPUT)
        gpio.pullup(self.GPIO_0,gpio.PULLUP)
        gpio.pullup(self.GPIO_1, gpio.PULLUP)
        
        self.continue_reading = True

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

    def processTag(self):
        if self.tag == "":
            return
        elif len(self.tag) < 10:
            print("[" + self.name + "] Frame of length (" + str(len(self.tag)) + "):" + self.tag + " DROPPED")
        elif self.verifyParity(self.tag):
            print("[" + self.name + "] Frame of length (" + str(len(self.tag)) + "): " + self.tag + " (" + str(self.binaryToInt(self.tag)) + ") OK KOI" )
        print("Tag : " + self.tag)

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
            print("[" + self.name + "] Frame of length (" + str(len(self.tag)) + "): " + self.tag + " (" + str(self.binaryToInt(self.tag)) + ") - PARITY CHECK FAILED")
            return False
        return True
            
    def run(self):
        while self.continue_reading:
            if gpio.input(self.GPIO_0) == 1:
                self.addBitToTag(self.GPIO_0)
            if gpio.input(self.GPIO_1) == 1:
                self.addBitToTag(self.GPIO_1)

    def binaryToInt(self, binary_string):
        print(binary_string)
        binary_string = binary_string[1:-1] #Removing the first and last bit (Non-data bits)
        print(binary_string)
        result = int(binary_string, 2)
        return result
    
            
    def end_read(self,signal,frame):
        pass
