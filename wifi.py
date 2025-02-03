import os

def add_wifi ():
    #Predifined networks in the format [SSID, Password]
    networks = [["2680-PSK", "poseidons3fork"], ["JB", "12345678"], ["Noiernet U", "Amperetime"]]

    for ssid,password in networks:
       
        os.system("sudo nmcli dev wifi connect "+ ssid +  " password " + password)