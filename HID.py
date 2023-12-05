# -*- coding: utf-8 -*-

import time
import DK_Keycodes
import UK_Keycodes

#Variables
NULL_CHAR = chr(0)

#Functions  
#Create write_report function to write HID codes to the HID Keyboard
def write_report(report):
    with open('/dev/hidg0', 'rb+') as fd:
        fd.write(report.encode())

buttons = {

    'enter':        40,     # ENTER
    'esc':          41,     # ESC
    'backspace':    42,     # BACKSPACE
    'tab':          43,     # TAB
    'delete':       76,     # DELETE
    'right':        79,     # Right
    'left':         80,     # Left
    'down':         81,     # Down
    'up':           82      # Up

}

# Modifier keys as hex:
# Left ctrl      = 01
# Left Shift     = 02
# Left alt       = 04
# Right ctrl     = 10
# Right shift    = 20
# Alt ctrl       = 40

modifier_values = {
    "ctrl": 1,
    "lctrl": 1,
    "shift": 2,
    "lshift": 2,
    "alt": 4,
    "lalt": 4,
    "rctrl": 16,
    "rshift": 32,
    "altctrl": 64
}

holds = {
    "ctrl":         False,
    "lctrl":        False,
    "shift":        False,
    "lshift":       False,
    "alt":          False,
    "lalt":         False,
    "rctrl":        False,
    "rshift":       False,
    "altctrl":      False
}

def skift_sprog (kode):
    if kode == "da_dk":
        key_lookup = DK_Keycodes.key_lookup_da_dk
    elif kode == "eng_uk":
        key_lookup = UK_Keycodes.key_lookup_eng_uk
    
    return key_lookup

key_lookup = DK_Keycodes.key_lookup_da_dk

def hold(key):
    holds[key] = True

def release(key):
    holds[key] = False

def get_modifier(combination = holds):
    modifier = 0
    for key, value in combination.items():
        if value:
            modifier += modifier_values[key]
    
    return modifier

def send_text(line):
    #Creates a list of keycodes
    keycodes = []

    for letter in line:
        if letter in key_lookup:
            keycodes.append(key_lookup[letter])
        else:
            print(letter)



    for k in keycodes:
        
        send_keypress(k)

    write_report(NULL_CHAR * 8)

def send_button(key):
    keycode = buttons[key]
    modifier = get_modifier()

    send_keypress([keycode, modifier])

def send_keypress(k):
    keycode = k[0]
    modifier = k[1]

    translated_keycode = chr(keycode)
    translated_modifier = chr(modifier)

    write_report(translated_modifier + NULL_CHAR + translated_keycode + NULL_CHAR*5)

    if (release):
        write_report(NULL_CHAR * 8)

    time.sleep(0.04) # skal være over 0.01

def parse_input(raw_input):
    lines = raw_input.split("\n")
    for line in lines:
        seperator = line.index(" ")
        mode = line[:seperator]
        content = line[seperator+1:]
        match mode:
            case "send":
                send_text(content)
            case "wait":
                time.sleep(int(content)/1000)
            case "button":
                send_button(content)
            case "hold":
                hold(content)
            case "release":
                release(content)
            case "sprog":
                skift_sprog(content)
        time.sleep(0.02)

