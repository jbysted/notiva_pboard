from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont
import shutil
import os
import psutil
import time
import subprocess #bare til at teste
import sys
import HID

# Function to be called when a button is pressed
def button_pressed(streamdeck, key, state):
    if state:

        if key == 0:
            load()
        else:
            print(f"Button {key} pressed.")

            path = "/home/pi/notiva_pboard/Streamdeck_Data"

            data = "temp"

            files = os.listdir(path)

            for file in files:
                if file == str(key)+".txt":
                    with open(path + "/" + file) as f:
                        data = f.read()
            
            if data == "temp" or data == "":
                alert(key, "No File")
            else:
                HID.parse_input(data)
            

# Find a StreamDeck, and open it
streamdecks = DeviceManager().enumerate()
if not streamdecks:
    raise Exception("No StreamDeck found")

deck = streamdecks[0]
deck.open()
deck.reset()

deck.set_key_callback(button_pressed)

def load():

    dst_path = "/home/pi/notiva_pboard/Streamdeck_Data"

    if not os.path.exists(dst_path): #Genererer en mappe i pboard mappen med som hedder Streamdeck_Data. Her bliver alt data lagt i
        os.makedirs(dst_path)

    drives = psutil.disk_partitions()


    if len(drives) < 3: #no usb
        alert(0, "Intet USB")

    else:
        #Removing existing files and directories
        if os.path.exists(dst_path+"/icons"):
            shutil.rmtree(dst_path+"/"+"icons")
        old_files = os.listdir(dst_path)
        for old in old_files:
            os.remove(dst_path + "/"+ old)

        alert(0,"Loader...")
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
            shutil.copy2(os.path.join(path+"/icons",icon), os.path.join(dst_path+"/icons",icon)) #Ryk alle billederne

        update_images()

    #todo: 0.png skal ikke overskrives!

    return

def update_images():
    for key in range(deck.key_count()):
        update_key_image(deck, key, False)

ASSETS_PATH = os.path.join("/home/pi/notiva_pboard/Streamdeck_Data", "icons")

def render_key_image(deck, icon_filename, label_text, key):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    try:
        icon = Image.open(icon_filename)
        image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])

        draw = ImageDraw.Draw(image)
        if key == 0:
            draw.text((image.width/2-len("Load")*3, image.height-20), text="Load", anchor="ms", fill="white")
        else:
            draw.text((image.width/2-len(str(key))*3, image.height-20), text=str(key), anchor="ms", fill="white")

        return PILHelper.to_native_format(deck, image)
    except:
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        if key == 0:
            draw.text((image.width/2-len("Loader")*3, image.height-20), text="Loader", anchor="ms", fill="white")
        else:
            draw.text((image.width/2-len(str(key))*3, image.height-20), text=str(key), anchor="ms", fill="white")
        return PILHelper.to_native_format(deck, image)


# Returns styling information for a key based on its position and state.
def get_key_style(deck, key, state):
    name = "Picture"
    icon = "{}.jpg".format(key)
    label = "Pressed!" if state else "Key {}".format(key)

    return {
        "name": name,
        "icon": os.path.join(ASSETS_PATH, icon),
        "label": label
    }


# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, key, state)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["label"],key)

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)

def alert(key, text):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, image.width, image.height), fill="black")
    draw.text((image.width/2-len(text)*3, image.height-20), str(text), fill="white", anchor="center")
    
    deck.set_key_image(key, PILHelper.to_native_format(deck, image))

    time.sleep(2)

    update_key_image(deck,key,False)

def start():

    alert(0, "Loader...")

    #load()
    update_images()

    try:
        print("Press a button on your Stream Deck...")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        deck.close()

start()