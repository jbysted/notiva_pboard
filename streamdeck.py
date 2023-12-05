#abc

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
            # Here you can call any function you want

            path = "/home/pboard/Streamdeck/Streamdeck_Data"

            data = "temp"

            files = os.listdir(path)

            for file in files:
                if file == str(key)+".txt":
                    with open(path + "/" + file) as f:
                        data = f.read()
            
            if data == "temp" or data == "":
                print_to_user(key, "No File")
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

    dst_path = "/home/pboard/Streamdeck/Streamdeck_Data"

    if not os.path.exists(dst_path): #Generere en mappe i pboard mappen med som hedder Streamdeck_Data. Her bliver alt data lagt i
        os.makedirs(dst_path)

    drives = psutil.disk_partitions()


    if len(drives) < 3: #no usb
        print_to_user(0, "Intet USB")

    else:
        #Removing existing files and directories
        if os.path.exists(dst_path+"/billeder"):
            shutil.rmtree(dst_path+"/"+"billeder")
        old_files = os.listdir(dst_path)
        for old in old_files:
            os.remove(dst_path + "/"+ old)

        print_to_user(0,"Loading")
        external = drives[2] #Får fat i det eksterne drev
        path = external[1] #Få fat i path til ekstern drev
        files = os.listdir(path) #Alle filer
        
        for file in files: #Gå igennem alle filer

            if file[-3:] == "txt": #Alle filer med txt extension
                shutil.copy2(os.path.join(path,file),os.path.join(dst_path,file)) #Ryk til destination på Pboard
    
        billeder = os.listdir(path+"/billeder") #Få fat i alle billederne
        if not os.path.exists(dst_path+"/billeder"): #Tjek om mappen allerede eksisterer på PBoard
                os.makedirs(dst_path+"/billeder") #Hvis ikke, lav den
        
        for billed in billeder: #Gå igennem alle billederne
            shutil.copy2(os.path.join(path+"/billeder",billed), os.path.join(dst_path+"/billeder",billed)) #Ryk alle billederne

        for key in range(deck.key_count()):
            update_key_image(deck, key, False)

    return

ASSETS_PATH = os.path.join("/home/pboard/Streamdeck/Streamdeck_Data", "billeder")

def render_key_image(deck, icon_filename, label_text,key):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    try:
        icon = Image.open(icon_filename)
        image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image a few pixels from the bottom of the key.
        draw = ImageDraw.Draw(image)
        if key == 0:
            draw.text((image.width - 55, image.height - 20), text="Loader", anchor="ms", fill="white")
        else:
            draw.text((image.width / 2, image.height - 20), text=str(key), anchor="ms", fill="white")

        return PILHelper.to_native_format(deck, image)
    except:
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)
        if key == 0:
            draw.text((image.width / 2, image.height - 40), text="Loader", anchor="ms", fill="white")
        else:
            draw.text((image.width / 2, image.height - 40), text=str(key), anchor="ms", fill="white")
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

def print_to_user(key, text):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, image.height), fill="black")
    draw.text((image.width - 55, image.height - 40), str(text), fill="white", anchor="center")
    
    deck.set_key_image(key, PILHelper.to_native_format(deck, image))

    time.sleep(2)

    update_key_image(deck,key,False)

def start():
    load()

    try:
        print("Press a button on your Stream Deck...")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        deck.close()

start()