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
from multiprocessing import Process
from threading import Thread
import threading

# Function to be called when a button is pressed
def button_pressed(streamdeck, key, state):
    if state: #If key is pressed
        if len(threading.enumerate()) >= 3: #If number of threads running is 3 or higher, PBoard is already doing an action
            return  #Disable any other actions
        else: # If number of threads are 2 or lower, deck is ready for a new action
            if key == 0: #If the load key (0) is pressed, create a thread with the load action
                thread = Thread(target = load)
                thread.start()
            else: #If any other key is pressed send the data instead
                thread = Thread(target = send_data, args = (streamdeck, key))
                thread.start()
            

def send_data(streamdeck,key): #Functions that reads and prepares data for the parse_input function

    print(f"Button {key} pressed.") #Debug statment

    path = "/home/pi/notiva_pboard/Streamdeck_Data" #Set the path of data

    data = "temp"

    files = os.listdir(path)

    for file in files:
        if file == str(key)+".txt":
            with open(path + "/" + file) as f:
                data = f.read()
    
    if data == "temp" or data == "":
        alert_timer(key, "No File")
    else:
        running_overlay(key) #Creates new overlay for streamdeck while running
        parse_input(data, key)
    
def parse_input(raw_input, key):
    lines = raw_input.split("\n")
    for line in lines:
        seperator = line.index(" ")
        mode = line[:seperator]
        content = line[seperator+1:]
        match mode:
            case "send":
                set_current_command("Writing", True)
                HID.send_text(content)
            case "wait":
                set_current_command("Waiting", True)
                time.sleep(int(content)/1000)
            case "button":
                HID.send_button(content)
            case "hold":
                HID.hold(content)
            case "release":
                HID.release(content)
            case "locale":
                HID.change_layout(content)
        time.sleep(0.02)
    set_current_command("Reset", False)

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
        alert_timer(0, "Intet USB")

    else:
        #Removing existing files and directories
        if os.path.exists(dst_path+"/icons"):
            old_images = os.listdir(dst_path+"/"+"icons")
            for image in old_images:
                if image != "0.jpg":
                    os.remove(dst_path+"/"+"icons" + "/" + image)
        old_files = os.listdir(dst_path)
        for old in old_files:
            if old[-3:] == "txt":
                os.remove(dst_path + "/"+ old)

        alert_timer(0,"Loader...")
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
            if icon != "0.jpg":
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

def alert_timer(key, text, timer = 2):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, image.width, image.height), fill="black")
    draw.text((image.width/2-len(text)*3, image.height-36), str(text), fill="white", anchor="center")
    
    deck.set_key_image(key, PILHelper.to_native_format(deck, image))

    time.sleep(timer)

    update_key_image(deck,key,False)

def draw_text(text):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, image.width, image.height), fill="black")
    draw.text((image.width/2-len(str(text))*3, image.height-36), str(text), fill="white", anchor="center")

    return image

def running_overlay(key):
    descriptive_text = ["Currently", "Running", "Macro", "Number", str(key)]
    for key in range(deck.key_count()):
        if key < 5: #Top row
            image = draw_text(descriptive_text[key])
            deck.set_key_image(key, PILHelper.to_native_format(deck, image))
        else:
            image = PILHelper.create_image(deck)
            draw = ImageDraw.Draw(image)

            draw.rectangle((0, 0, image.width, image.height), fill="black")
            deck.set_key_image(key, PILHelper.to_native_format(deck, image))

def set_current_command(text, running = False):
    if running:
        image = draw_text(text)
        deck.set_key_image(7, PILHelper.to_native_format(deck, image))
    else:
        update_images()
    
    return running


def start():

    alert_timer(0, "Loader...")

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