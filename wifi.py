import os
from server import host

def add_wifi ():
    #Predifined networks in the format [SSID, Password]
    networks = [["2680-PSK", "poseidons3fork"], ["JB", "12345678"], ["Noiernet U", "Amperetime"]]

    for ssid,password in networks:
        if not host.internet_connection():
            os.system("sudo nmcli dev wifi connect "+ ssid +  " password " + password)
        else:
             return