import os

class ReadWifiCredentials:
    def read(self):
        wifi_info_file = open(os.getcwd() + "/config/wifi.txt", "r")
        readed_lines = wifi_info_file.readlines()
        interface_name = readed_lines[0].split(' ')[1].replace('\n', '')
        ssid = readed_lines[1].split(' ')[1].replace('\n', '')
        wifi_pass = readed_lines[2].split(' ')[1].replace('\n', '')
        return {
            "ssid": ssid,
            "password": wifi_pass,
            "interface_name": interface_name
        }
