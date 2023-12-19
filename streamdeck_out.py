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
import socket
import re as r
import json
import requests


def set_deck(streamdeck):
    global deck
    deck = streamdeck

def set_states(the_states):
    global states
    states = the_states

def update_states(new_states):
    global states
    states = new_states



def send_data(key): #Functions that reads and prepares data for the parse_input function

    print(f"Button {key} pressed.") #Debug statment

    path = "/home/pi/New_notiva_pboard/Streamdeck_Data/macro_keyboard" #Set the path of data

    data = "temp"

    files = os.listdir(path)

    for file in files:
        if file == str(key)+".txt":
            with open(path + "/" + file) as f:
                data = f.read()
    
    if data == "temp" or data == "":
        alert_timer(deck, key, "No File")
        return False
    else:
        running_overlay(deck, key) #Creates new overlay for streamdeck while running
        parse_input(data)


def server_input(raw_input):
    lines = raw_input.split("\n")
    key_layout = HID.change_layout("da_dk")
    for line in lines:
        seperator = line.index(" ")
        mode = line[:seperator]
        content = line[seperator+1:]
        match mode:
            case "send":
                HID.send_text(content, key_layout)
            case "wait":
                time.sleep(int(content)/1000)
            case "button":
                HID.send_button(content)
            case "hold":
                HID.hold(content)
            case "release":
                HID.release(content)
            case "locale":
                key_layout = HID.change_layout(content)
        time.sleep(0.02)


def parse_input(raw_input):
    print ("parse input activated")
    lines = raw_input.split("\n")
    key_layout = HID.change_layout("da_dk")
    for line in lines:
        seperator = line.index(" ")
        mode = line[:seperator]
        content = line[seperator+1:]
        match mode:
            case "send":
                print ("Send case found")
                set_current_command(deck, "Writing", True)
                print("delegating to HID")
                HID.send_text(content, key_layout)
            case "wait":
                set_current_command(deck, "Waiting", True)
                time.sleep(int(content)/1000)
            case "button":
                HID.send_button(content)
            case "hold":
                HID.hold(content)
            case "release":
                HID.release(content)
            case "locale":
                key_layout = HID.change_layout(content)
        time.sleep(0.02)
    set_current_command(deck, "Reset", False)



def update_images(deck, return_key = None):
    for key in range(deck.key_count()):
        if key == return_key:
            update_key_image(deck, "return", key)
        else:
            update_key_image(deck, key, key)

def render_key_image(deck, icon_filename, label_text, key):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    try:
        icon = Image.open(icon_filename)
        image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])

        draw = ImageDraw.Draw(image)
        if key == 0:
            draw.text((image.width/2-len("Return")*3, image.height-20), text="Return", anchor="ms", fill="white")
        else:
            draw.text((image.width/2-len(str(label_text))*3, image.height-20), text=str(label_text), anchor="ms", fill="white")

        return PILHelper.to_native_format(deck, image)
    except:
        pass


# Returns styling information for a key based on its position and state.
def get_key_style(deck, filename, key):

    if states["macro"] and filename != "return":
        ASSETS_PATH = os.path.join("/home/pi/notiva_pboard/Streamdeck_Data/macro_keyboard/", "icons")
    else:
        ASSETS_PATH = os.path.join("/home/pi/notiva_pboard/Streamdeck_Data", "menu_icons")


    name = "Picture"
    icon = "{}.jpg".format(filename)

    return {
        "name": name,
        "icon": os.path.join(ASSETS_PATH, icon),
        "label": filename
    }

# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.
def update_key_image(deck, name, key):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(deck, name, key)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, key_style["icon"], key_style["label"],key)

    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key, image)

def alert_timer(deck, key, text, timer = 2):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, image.width, image.height), fill="black")
    draw.text((image.width/2-len(text)*3, image.height-36), str(text), fill="white", anchor="center")
    
    deck.set_key_image(key, PILHelper.to_native_format(deck, image))

    time.sleep(timer)

    if states["macro"]:
        update_key_image(deck,key,key)
    
    if states["load"] and key in range(6,8):
        names = ["0", "macro data"]
        update_key_image(deck, names[key-6], key)

    else:
        image = PILHelper.create_image(deck)
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, image.width, image.height), fill="black")
        deck.set_key_image(key, PILHelper.to_native_format(deck, image))
        

def draw_text(deck, text):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, image.width, image.height), fill="black")
    draw.text((image.width/2-len(str(text))*3, image.height-36), str(text), fill="white", anchor="center")

    return image

def running_overlay(deck, key):
    descriptive_text = ["Currently", "Running", "Macro", "Number", str(key)]
    for key in range(deck.key_count()):
        if key < 5: #Top row
            image = draw_text(deck, descriptive_text[key])
            deck.set_key_image(key, PILHelper.to_native_format(deck, image))
        else:
            image = PILHelper.create_image(deck)
            draw = ImageDraw.Draw(image)

            draw.rectangle((0, 0, image.width, image.height), fill="black")
            deck.set_key_image(key, PILHelper.to_native_format(deck, image))

def set_current_command(deck, text, running = False):
    if running:
        image = draw_text(deck,text)
        deck.set_key_image(7, PILHelper.to_native_format(deck, image))
    else:
        update_images(deck, return_key=0)
    
    return running

def start_menu(deck):
    names = ["server", "macro", "load"]
    for key in range(deck.key_count()):
        if key in range(6,9):
            update_key_image(deck, names[key-6], key)
        else:
            image = PILHelper.create_image(deck)
            draw = ImageDraw.Draw(image)

            draw.rectangle((0, 0, image.width, image.height), fill="black")
            deck.set_key_image(key, PILHelper.to_native_format(deck, image))

def macro_menu(deck):
    update_images (deck,return_key=0)

def load_menu(deck):
    names = ["load", "macro data"]
    for key in range(deck.key_count()):
        if key in range(6,8):
            update_key_image(deck, names[key-6], key)
        else:
            image = PILHelper.create_image(deck)
            draw = ImageDraw.Draw(image)

            draw.rectangle((0, 0, image.width, image.height), fill="black")
            deck.set_key_image(key, PILHelper.to_native_format(deck, image))
    
    update_key_image(deck,"return",0)

def server_menu (deck, connection, ip = None):
    global server

    bottom_row = ["IP:"]
    status = ["Connection:"]
    online = connection
    if online:
        status.append("Online")
        for number in ip.split("."):
            bottom_row.append(number)

        for key in range(deck.key_count()):
            if key in range(10,15):
                image = draw_text(deck, bottom_row[key-10])
                deck.set_key_image(key, PILHelper.to_native_format(deck, image))
            elif key in range(1,3):
                image = draw_text(deck, status[key-1])
                deck.set_key_image(key, PILHelper.to_native_format(deck, image))
            else:
                image = PILHelper.create_image(deck)
                draw = ImageDraw.Draw(image)

                draw.rectangle((0, 0, image.width, image.height), fill="black")
                deck.set_key_image(key, PILHelper.to_native_format(deck, image))

        update_key_image(deck,"return",0) 
    else:
        status.append("Offline")
        bottom_row.append("None")

        for key in range(deck.key_count()):
            if key in range(10,12):
                image = draw_text(deck, bottom_row[key-10])
                deck.set_key_image(key, PILHelper.to_native_format(deck, image))
            elif key in range(1,3):
                image = draw_text(deck, status[key-1])
                deck.set_key_image(key, PILHelper.to_native_format(deck, image))
            else:
                image = PILHelper.create_image(deck)
                draw = ImageDraw.Draw(image)

                draw.rectangle((0, 0, image.width, image.height), fill="black")
                deck.set_key_image(key, PILHelper.to_native_format(deck, image))

        update_key_image(deck,"return",0) 
          
