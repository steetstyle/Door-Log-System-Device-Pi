import sys
import os
sys.path.append(os.getcwd())
from helpers.wifi import Finder
from helpers.read_wifi_credentials import ReadWifiCredentials
from config import channel_list
import OPi.GPIO as GPIO
from time import sleep
from helpers.CardReader import CardReader
import signal

class App:

    continue_reading = False

    BIT_TRANSMISSION_TIME = 0.002 #From wiegand specification
    FRAMESIZE = 48 #Supposed size of received frame
    FRAMETIME = FRAMESIZE * BIT_TRANSMISSION_TIME #Theoric time necessary to transfer a frame
    ALLOWANCE = 10 #Auhtorized allowance for the transmission time in percent
    TIMEOUT = FRAMETIME*(1+ALLOWANCE/100) #Real time allowed for the transmission

    reader_list = []

    def __init__(self):
        self.setup()

    def setup(self):
        wifi_credentials = ReadWifiCredentials().read()
        F = Finder(server_name=wifi_credentials['ssid'],
                password=wifi_credentials['password'],
                interface=wifi_credentials['interface_name'])
        F.run()

        # Hook the SIGINT
        signal.signal(signal.SIGINT, self.end_read)
        self.continue_reading = True
        GPIO.setmode(GPIO.BOARD)

        self.readersList = [
            CardReader("reader", GPIO.PA+1, GPIO.PA+11, self.TIMEOUT),
        ]

        #Starting readers
        readersCount = 1
        for reader in self.readersList:
            print("Initializing reader " + str(readersCount) + "...")
            reader.registerReader()
            print(" Done !")
            readersCount += 1

    def run(self):
        while self.continue_reading:
            pass        
            
    def end_read(self,signal,frame):
        print("Ctrl+C captured, ending read.")
        self.continue_reading = False
        GPIO.cleanup()
