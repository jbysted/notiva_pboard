import os

def first_time_config():
    config_lines = [
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'update_config=1',
        'country=DK',
        '\n'
    ]

    config = '\n'.join(config_lines)

    #give access and writing. may have to do this manually beforehand
    os.popen("sudo chmod a+w /etc/wpa_supplicant/wpa_supplicant.conf")
    
    #writing to file
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        wifi.write(config)
    
    print("Wifi config added. Refreshing configs")
    ## refresh configs
    os.popen("sudo wpa_cli -i wlan0 reconfigure")


def configure_wifi(ssid, password):
    config_lines = [
        'network={',
        '\tssid="{}"'.format(ssid),
        '\tpsk="{}"'.format(password),
        '}',
        '\n'
        ]
    config = '\n'.join(config_lines)
    
    #give access and writing. may have to do this manually beforehand
    os.popen("sudo chmod a+w /etc/wpa_supplicant/wpa_supplicant.conf")
    
    #writing to file
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as wifi:
        wifi.write(config)
    
    print("Wifi config added. Refreshing configs")
    ## refresh configs
    os.popen("sudo wpa_cli -i wlan0 reconfigure")

def add_wifi ():
    first_time_config()

    #Predifined networks in the format [SSID, Password]
    networks = [["2680-PSK", "poseidons3fork"], ["JB", "12345678"], ["Noiernet U", "Amperetime"]]
    for ssid,password in networks:
        configure_wifi(ssid,password)