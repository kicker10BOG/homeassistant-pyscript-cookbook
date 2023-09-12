# import from module if needed
from jason import *

# list of buttons on the remote.
# If you have multiple remotes with different amounts of buttons, each will need its own list
buttons = ["001", "002", "003", "004"]

# the button factory. It sets up the triggers and performs the actions
# param nodeId: the z-wave node_id to listen for
# param buttons: the list of buttons
# param sequences: the actions to perform for each specific sequence of button presses
# param tracker: a text_input helper entity that keeps track of the current sequence
# param waitTime: the number of seconds to wait for continued input
def zwave_remote_setup(nodeId, buttons, sequences, tracker, waitTime = 1):
    # set the tracker to empty
    state.set(tracker, "")

    # define trigger and how to handle it. 
    @event_trigger("zwave_js_value_notification", f"node_id == {nodeId}")
    def handle_command(**kwargs):
        try:
            # only accept single press. 
            # 1 and 2 are hold and release. reset on those
            if kwargs['value_raw'] != 0:
                state.set(tracker, "")
            else: 
                currentSequence = state.get(tracker)
                sequenceArray = []
                if currentSequence != "":
                    sequenceArray = currentSequence.split(",")
                # add button press to sequence
                sequenceArray.append(kwargs['property_key'])
                state.set(tracker, ",".join(sequenceArray))
                # get the action to be performed if the sequence ends here
                indicies = [buttons.index(buttonPush) for buttonPush in sequenceArray]
                action = sequences[indicies[0]] 
                for index in indicies[1:]:
                    action = action[1][index] 
                
                # wait waitTime seconds for another button press
                waitForPress = task.wait_until(
                    timeout=waitTime,
                    event_trigger=("zwave_js_value_notification", f"node_id == {nodeId}"),
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
            # if error, reset
            state.set(tracker, "")

    return handle_command

# define functions to be called

# a function to do nothing, used for sequences you don't want to do anything on
def pass_func():
    return None

def turnOnMonitors():
    service.call("pyscript", "turn_on_monitors")
def turnOffMonitors():
    service.call("pyscript", "turn_off_monitors")
def toggle_monitors():
    service.call("pyscript", "toggle_monitors")

def toggle_ultrawide():
    switch.toggle(entity_id=ultrawide)
def toggle_touchscreen():
    switch.toggle(entity_id=touchscreen)
def toggle_normal():
    switch.toggle(entity_id=normalmonitor)

def toggle_lock():
    lockState = state.get(jason_lock)
    if lockState == "locked":
        service.call("lock", "unlock", entity_id=jason_lock)
    else: 
        service.call("lock", "lock", entity_id=jason_lock)

def toggle_lr_light():
    light.toggle(entity_id=lrlight)
def lr_light_to_25():
    light.turn_on(entity_id=lrlight, brightness=64)
def lr_light_to_50():
    light.turn_on(entity_id=lrlight, brightness=128)
def lr_light_to_75():
    light.turn_on(entity_id=lrlight, brightness=192)
def lr_light_to_100():
    light.turn_on(entity_id=lrlight, brightness=255)

def toggle_h_light():
    light.toggle(entity_id=hlight)
def h_light_to_25():
    light.turn_on(entity_id=hlight, brightness=64)
def h_light_to_50():
    light.turn_on(entity_id=hlight, brightness=128)
def h_light_to_75():
    light.turn_on(entity_id=hlight, brightness=192)
def h_light_to_100():
    light.turn_on(entity_id=hlight, brightness=255)

def toggle_br_light():
    light.toggle(entity_id=brlight)
def br_light_to_25():
    light.turn_on(entity_id=brlight, brightness=64)
def br_light_to_50():
    light.turn_on(entity_id=brlight, brightness=128)
def br_light_to_75():
    light.turn_on(entity_id=brlight, brightness=192)
def br_light_to_100():
    light.turn_on(entity_id=brlight, brightness=255)

def toggle_lr_fan():
    service.call("fan", "toggle", entity_id=jason_lr_fan)
def increase_lr_fan_speed():
    service.call("fan", "increase_speed", entity_id=jason_lr_fan)
def decrease_lr_fan_speed():
    service.call("fan", "decrease_speed", entity_id=jason_lr_fan)

def toggle_br_fan():
    service.call("fan", "toggle", entity_id=jason_br_fan)
def increase_br_fan_speed():
    service.call("fan", "increase_speed", entity_id=jason_br_fan)
def decrease_br_fan_speed():
    service.call("fan", "decrease_speed", entity_id=jason_br_fan)

def good_night_jason():
    service.call("pyscript", "good_night_jason")
def good_morning_jason():
    service.call("pyscript", "good_morning_jason")

# define sequences and their actions 
lr_wallmot_sequences = [
    [
        toggle_lr_light, #1
        [
            lr_light_to_25, #1,1
            lr_light_to_50, #1,2
            lr_light_to_75, #1,3
            lr_light_to_100, #1,4
        ]
    ],
    [
        toggle_h_light, #2
        [
            h_light_to_25, #2,1
            h_light_to_50, #2,2
            h_light_to_75, #2,3
            h_light_to_100, #2,4
        ]
    ],
    [
        pass_func, #3
        [
            pass_func, #3,1
            pass_func, #3,2
            [
                toggle_monitors, #3,3
                [
                    toggle_ultrawide, #3,3,1
                    toggle_normal, #3,3,2
                    pass_func, #3,3,3
                    toggle_touchscreen, #3,3,4
                ]
            ],
            pass_func, #3,4
        ]
    ],
    [
        pass_func, #4
            [
                increase_lr_fan_speed, #4,1
                toggle_lr_fan, #4,2
                decrease_lr_fan_speed, #4,3
                toggle_lock #4,4
            ]
    ] 
]

# setup buttons
jason_lr_wallmote_ref = zwave_remote_setup(wallmote, wallmote_buttons, lr_wallmot_sequences, wallmote_tracker)
