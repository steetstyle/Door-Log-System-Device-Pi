import sys
import os
sys.path.append(os.getcwd())
from helpers.wifi import Finder
from helpers.read_wifi_credentials import ReadWifiCredentials
import OPi.GPIO as GPIO
from time import sleep         

        
class App:
    def __init__(self):
        self.setup()
        

    def setup(self):
        wifi_credentials = ReadWifiCredentials().read()
        F = Finder(server_name=wifi_credentials['ssid'],
                password=wifi_credentials['password'],
                interface=wifi_credentials['interface_name'])
        F.run()
        GPIO.setboard(GPIO.ZERO)    # Orange Pi PC board
        GPIO.setmode(GPIO.BOARD)        # set up BOARD BCM numbering
        GPIO.setup(7, GPIO.OUT)

    def run(self):
        try:
            print ("Press CTRL+C to exit")
            while True:
                print('naber')
                sleep(1)

                

        except KeyboardInterrupt:
            GPIO.output(7, 0)           # set port/pin value to 0/LOW/False
            GPIO.cleanup()              # Clean GPIO
            print ("Bye.")
