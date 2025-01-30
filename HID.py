import time
import da_dk_keycodes
import en_uk_keycodes

#Variables
NULL_CHAR = chr(0)
USB = True

#Create write_report function to write HID codes to the HID Keyboard
def write_report(report):
    try:
        with open('/dev/hidg0', 'rb+') as fd:
            fd.write(report.encode())
    except Exception as e: #If it could not write to the USB, it means nothing is connected.
        print(e)
        global USB
        USB = False #Set the Flag for USB to False

buttons = {
    'enter':        40,     # ENTER
    'esc':          41,     # ESC
    'backspace':    42,     # BACKSPACE
    'tab':          43,     # TAB
    'delete':       76,     # DELETE
    'right':        79,     # RIGHT
    'left':         80,     # LEFT
    'down':         81,     # DOWN
    'up':           82      # UP
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

def change_layout (locale):
    if locale == "da_dk":
        key_lookup = da_dk_keycodes.key_lookup_da_dk
    elif locale == "en_uk":
        key_lookup = en_uk_keycodes.key_lookup_en_uk
    
    return key_lookup

key_lookup = da_dk_keycodes.key_lookup_da_dk

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

def send_text(line, key_lookup):
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

    time.sleep(0.02) # Must be above .01