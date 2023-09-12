# import from modules if needed
from greatRoom import *

# list of buttons on the remote.
# If you have multiple remotes with different amounts of buttons, each will need its own list
buttons = [
    "1",
    "2",
    "3",
    "4",
]

# list of possible actions for the remotes I have
# actions_available = [
#     "1_single",
#     "1_double",
#     "1_hold",
#     "2_single",
#     "2_double",
#     "2_hold",
#     "3_single",
#     "3_double",
#     "3_hold",
#     "4_single",
#     "4_double",
#     "4_hold",
# ]

# the button factory. It sets up the triggers and performs the actions
# param topic: the mqtt topic to listen for
# param buttons: the list of buttons
# param sequences: the actions to perform for each specific sequence of button presses
# param tracker: a text_input helper entity that keeps track of the current sequence
# param waitTime: the number of seconds to wait for continued input
def zigbee2mqtt_button_factory(topic, buttons, sequences, tracker, waitTime = 1):
    # set the tracker to empty
    state.set(tracker, "")

    # define trigger and how to handle it. 
    @mqtt_trigger(topic)
    def handle_command(**kwargs):
        # get the payload and determine which button was pressed and the action type (single, double, hold)
        payload = json.loads(kwargs['payload'])
        action = payload['action']
        button, actionType = action.split('_')
        try:
            # if "hold" then reset this sequence
            if actionType == "hold":
                state.set(tracker, "")
            else:
                currentSequence = state.get(tracker)
                sequenceArray = []
                if currentSequence != "":
                    sequenceArray = currentSequence.split(",")
                # add button press to sequence
                sequenceArray.append(button)
                # treat double tap as two taps
                if actionType == "double":
                    sequenceArray.append(button)
                state.set(tracker, ",".join(sequenceArray))
                # get the action to be performed if the sequence ends here
                indicies = [buttons.index(buttonPush) for buttonPush in sequenceArray]
                action = sequences[indicies[0]] 
                for index in indicies[1:]:
                    action = action[1][index] 

                # wait waitTime seconds for another button press
                waitForPress = task.wait_until(
                    timeout=waitTime,
                    mqtt_trigger=(topic),
                    state_check_now=False
                )

                # if not pressed, execute the action
                if waitForPress['trigger_type'] == 'timeout':
                    state.set(tracker, "")
                    if callable(action):
                        action()
                    else:
                        action[0]()
        except:
            #if error, reset
            state.set(tracker, "")
    
    return handle_command

# define functions to be called

# a function to do nothing, used for sequences you don't want to do anything on
def pass_func():
    return None

def toggle_chaise_light():
    light.toggle(entity_id=chaise_light)
def turn_off_chaise_fan():
    service.call("fan", "turn_off", entity_id=chaise_fan)
def increase_chaise_fan_speed():
    service.call("pyscript", "bond_chaise_fan_increase_speed")
def decrease_chaise_fan_speed():
    service.call("pyscript", "bond_chaise_fan_decrease_speed")
    
def toggle_couch_light():
    light.toggle(entity_id=couch_light)
def turn_off_couch_fan():
    service.call("fan", "turn_off", entity_id=couch_fan)
def increase_couch_fan_speed():
    service.call("pyscript", "bond_couch_fan_increase_speed")
def decrease_couch_fan_speed():
    service.call("pyscript", "bond_couch_fan_decrease_speed")

def toggle_dining_room_light():
    light.toggle(entity_id=dining_room_light)
def turn_off_dining_room_fan():
    service.call("fan", "turn_off", entity_id=dining_room_fan)
def increase_dining_room_fan_speed():
    service.call("pyscript", "bond_dining_room_fan_increase_speed")
def decrease_dining_room_fan_speed():
    service.call("pyscript", "bond_dining_room_fan_decrease_speed")

def toggle_great_room_light():
    service.call("pyscript", "lr_turn_off_lights")
def turn_off_great_room_fan():
    service.call("pyscript", "lr_turn_off_fans")
def increase_great_room_fan_speed():
    service.call("pyscript", "bond_great_room_fan_increase_speed")
def decrease_great_room_fan_speed():
    service.call("pyscript", "bond_great_room_fan_decrease_speed")

def kitchen_shades_to_blackout():
    service.call("pyscript", "set_kitchen_shades_to_full_blackout")
def kitchen_shades_to_sheer():
    service.call("pyscript", "set_kitchen_shades_to_full_sheer")
def kitchen_shades_to_open():
    service.call("pyscript", "set_kitchen_shades_to_full_open")
def kitchen_shades_stop():
    service.call("pyscript", "stop_kitchen_shade_movement")

# define sequences and their actions 
jason_chaise_remote_sequences = [
    [
        toggle_chaise_light, #1
        [
            increase_chaise_fan_speed, #1,1
            decrease_chaise_fan_speed, #1,2
            pass_func, #1,3
            turn_off_chaise_fan #1,4
        ]
    ],
    [
        toggle_couch_light, #2
        [
            increase_couch_fan_speed, #2,1
            decrease_couch_fan_speed, #2,2
            pass_func, #2,3
            turn_off_couch_fan #2,4
        ]
    ],
    [
        toggle_dining_room_light, #3
        [
            increase_dining_room_fan_speed, #3,1
            decrease_dining_room_fan_speed, #3,2
            [
                pass_func, #3,3
                [
                    kitchen_shades_to_blackout, #3,3,1
                    kitchen_shades_to_sheer, #3,3,2
                    kitchen_shades_to_open, #3,3,3
                    kitchen_shades_stop, #3,3,4
                ]
            ],
            turn_off_dining_room_fan #3,4
        ]
    ],
    [
        toggle_great_room_light, #4
        [
            increase_great_room_fan_speed, #4,1
            decrease_great_room_fan_speed, #4,2
            pass_func, #4,3
            turn_off_great_room_fan #4,4
        ]
    ],
]

# setup buttons
jason_chaise_remote_ref = zigbee2mqtt_button_factory("homeassistant/zigbee2mqtt/jason_chaise_remote", buttons, jason_chaise_remote_sequences, jason_chaise_remote_tracker)
