from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont
import streamdeck_out as out
from threading import Thread
import threading
import makro
from server import host
import time
from multiprocessing import Process

# Function to be called when a button is pressed
def button_pressed(streamdeck, key, state):
    global states
    global server #The server thread


    if states["start"] and state: #Check if the start menu is on
        if key not in range(6,9): #If you dont press on of the menues on key 6,7,8
            thread = Thread(target=out.alert_timer, args = (deck, key,"Pick Option")) #Alert the user
            thread.start()
        else: #If they choose a menu
            if key == 6: #Server menu
                states["start"] = False #Set start boolean to false
                states["server"] = True #Set server boolean to True
                out.update_states(states)
                connection = host.internet_connection() #Checks if the device is connected
                if connection:
                    ip = host.getIP()
                    server = Process(target = host.start, args=([ip])) #Start the server on that IP
                    server.start()
                    out.server_menu(deck, connection, ip) #Intiate the server menu
                else:
                    out.server_menu(deck, connection)



            elif key == 7: #Macro Keyboard Menu
                states["start"] = False
                states["macro"] = True
                out.update_states(states)
                out.macro_menu(deck)

            elif key == 8: #Load Menu
                states["start"] = False
                states["load"] = True
                out.update_states(states)
                out.load_menu(deck)
    
    if states["server"] and state: #If the server menu is on
        if key == 0: #If the return key is pressed
            states["start"] = True #And set booleans again
            states["server"] = False
            out.update_states(states)
            try:
                server.terminate() #Terminate the process that holds the web server
            except:
                pass
            out.start_menu(deck) #Reload the start menu
        else: #All other buttons are disabled
            return
    
    if states["load"] and state: #If the load menu is on
        if key == 0: #Return key
            if len(threading.enumerate()) >= 3: #Wait for all threads to finish before loading next menu
                for thread in threading.enumerate():
                    if thread.getName()[-13:] == "(alert_timer)":
                        thread.join()
            states["start"] = True
            states["load"] = False
            out.update_states(states)
            out.start_menu(deck) #Reload start menu

        elif key == 6: #Load all data button
            succed = makro.load_makro(key) #To do: skal load alt data
            if succed:
                states["load"] = False
                states["macro"] = True
                out.update_states(states)
                out.macro_menu(deck)

        elif key == 7: #Load Macro data button
            succed = makro.load_makro(key) #To do: Skal kun load data til Macro keyboard
            if succed:
                states["load"] = False
                states["macro"] = True
                out.update_states(states)
                out.update_images(deck, return_key=0)
                out.macro_menu(deck)

        else: #All other keys
            thread = Thread(target=out.alert_timer, args = (deck, key,"Pick Option")) #Alert user
            thread.start()
    
    if states["macro"] and state: #If macro menu is on
        if len(threading.enumerate()) >= 3: #If number of threads running is 3 or higher, PBoard is already doing an action
            return  #Disable any other actions
        
        else: # If number of threads are 2 or lower, deck is ready for a new action
            if key == 0: #Return key
                if len(threading.enumerate()) >= 3: #Wait for all threads to finish before loading next menu
                    for thread in threading.enumerate():
                        if thread.getName()[-13:] == "(alert_timer)":
                            thread.join()
                states["start"] = True
                states["macro"] = False
                out.update_states(states)
                out.start_menu(deck) #Reload start menu
            else: #If any other key is pressed send the data instead
                thread = Thread(target = out.send_data, args = [key])
                thread.start()
                    


def start(deck):

    out.render_key_image(deck,"/home/pi/notiva_pboard/Streamdeck_Data/menu_icons/0.jpg", "test",0)

    out.set_deck(deck)
    makro.set_deck(deck)
    out.set_states(states)

    out.start_menu(deck)

    #load()
    #update_images()

    try:
        print("Press a button on your Stream Deck...")
        while True:
            if out.states["reset"]: #If the call to reset is given, reset the script
                print("Reset command given, resetting")
                return
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        deck.close()

# Find a StreamDeck, and open it
streamdecks = DeviceManager().enumerate()
if not streamdecks:
    raise Exception("No StreamDeck found")

deck = streamdecks[0]
deck.open()
deck.reset()

deck.set_key_callback(button_pressed)

states = {"start": True, "load": False, "macro": False, "server": False, "reset": False}
start(deck)

while out.states["reset"]: #If the reset command was given, rerun the script
    states = {"start": True, "load": False, "macro": False, "server": False, "reset": False} # Set the states again
    deck = streamdecks[0] #Get the streamdeck
    deck.open()
    deck.reset()
    print("Reset Complete")
    start(deck) #And start it once again