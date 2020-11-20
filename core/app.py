import sys
import os
sys.path.append(os.getcwd())
from helpers.wifi import Finder
from helpers.read_wifi_credentials import ReadWifiCredentials
from config import channel_list
import OPi.GPIO as GPIO
from time import sleep
from helpers.MFRC522 import MFRC522
import signal

class App:

    continue_reading = False
    MIFAREReader = MFRC522()

    def __init__(self):
        self.setup()

    def setup(self):
        wifi_credentials = ReadWifiCredentials().read()
        F = Finder(server_name=wifi_credentials['ssid'],
                password=wifi_credentials['password'],
                interface=wifi_credentials['interface_name'])
        F.run()
        
        GPIO.setup(channel_list.high_channel_in_list, GPIO.IN, initial=GPIO.LOW)
        GPIO.setup(channel_list.high_channel_out_list, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(channel_list.low_channel_in_list, GPIO.IN, initial=GPIO.LOW)
        GPIO.setup(channel_list.low_channel_out_list, GPIO.OUT, initial=GPIO.HIGH)


        # Hook the SIGINT
        signal.signal(signal.SIGINT, self.end_read)
        self.continue_reading = True


    def run(self):
        try:
            print("Press CTRL+C to exit")
            # This loop keeps checking for chips. If one is near it will get the UID and authenticate
            while self.continue_reading:
                # Scan for cards    
                (status,TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)
                
                # If a card is found
                if status == self.MIFAREReader.MI_OK:
                    print("Card detected")
                
                (status, uid) = self.MIFAREReader.MFRC522_Anticoll()
                
                # If we have the UID, continue
                if status == self.MIFAREReader.MI_OK:
                    # Print UID
                    print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

                # This is the default key for authentication
                key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

                # Select the scanned tag
                self.MIFAREReader.MFRC522_SelectTag(uid)

                # Authenticate
                status = self.MIFAREReader.MFRC522_Auth(self.MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

                # Check if authenticated
                if status == self.MIFAREReader.MI_OK:
                    self.MIFAREReader.MFRC522_Read(8)
                    self.MIFAREReader.MFRC522_StopCrypto1()
                else:
                    print("Authentication error")

        except KeyboardInterrupt:
            GPIO.output(7, 0)           # set port/pin value to 0/LOW/False
            GPIO.cleanup()              # Clean GPIO
            print("Bye.")
            
    def end_read(self,signal,frame):
        print("Ctrl+C captured, ending read.")
        self.continue_reading = False
        GPIO.cleanup()
