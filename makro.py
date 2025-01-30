
import os
import streamdeck_out as out
import psutil
import shutil


def set_deck(streamdeck):
    global deck
    deck = streamdeck

def load_makro(key):

    dst_path = "/home/pi/notiva_pboard/Streamdeck_Data/macro_keyboard"

    if not os.path.exists(dst_path): #Genererer en mappe i pboard mappen med som hedder macro_keyboard i Streamdeck_Data. Her bliver alt data lagt i
        os.makedirs(dst_path)

    drives = psutil.disk_partitions()


    if len(drives) < 3: #no usb
        out.alert_timer(deck, key, "Intet USB")
        return False

    else:
        constants = ["0.jpg", "server.jpg", "macro.jpg", "return.jpg"]
        #Removing existing files and directories
        if os.path.exists(dst_path+"/icons"):
            old_images = os.listdir(dst_path+"/"+"icons")
            for image in old_images:
                if image not in constants:
                    os.remove(dst_path+"/"+"icons" + "/" + image)
        old_files = os.listdir(dst_path)
        for old in old_files:
            if old[-3:] == "txt":
                os.remove(dst_path + "/"+ old)

        out.alert_timer(deck, key,"Loader...")

        external = drives[2] #Får fat i det eksterne drev
        path = external[1] #Få fat i path til ekstern drev
        files = os.listdir(path) #Alle filer
        
        for file in files: #Gå igennem alle filer

            if file[-3:] == "txt": #Alle filer med txt extension
                shutil.copy2(os.path.join(path,file),os.path.join(dst_path,file)) #Ryk til destination på Pboard
    
        icons = os.listdir(path+"/icons") #Få fat i alle billederne
        if not os.path.exists(dst_path+"/icons"): #Tjek om mappen allerede eksisterer på PBoard
                os.makedirs(dst_path+"/icons") #Hvis ikke, lav den
        
        for icon in icons: #Gå igennem alle billederne
            if icon == "14.jpg":
                continue
            if icon not in constants:
                shutil.copy2(os.path.join(path+"/icons",icon), os.path.join(dst_path+"/icons",icon)) #Ryk alle billederne

    return True