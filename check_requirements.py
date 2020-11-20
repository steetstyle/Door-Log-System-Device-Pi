#!/usr/bin/python

import sys, getopt, os
import subprocess
import importlib
import runpy
def main(argv):
    os.system('sudo apt-get install python3-pip')
    os.system('sudo pip3 install --upgrade OPi.GPIO')
    os.system('sudo pip3 install ./libraries/SPI-Py')

if __name__ == "__main__":
   main(sys.argv[1:])