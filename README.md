# homeassistant-pyscript-cookbook
helpful functions to use in pyscript in home assistant

## z-wave
### buttonFactory
This code helps you setup z-wave remotes to listen for any sequence of button pushes and then performs the specified action.
I have tested it with two Aotec Wallmote Quads and an Aotec Nanomote Quad using the zwavejs2mqtt add-on. 
It works great for me. 

## zigbee2mqtt
### buttonFactory
This code helps you setup zigbee2mqtt remotes to listen for any sequence of button pushes and then performs the specified action.
I have tested it with a couple of Tuya zigbee devices. 
Instead of using the zigbee2mqtt add-on, I have zigbee2mqtt running on a different computer, which might be why it has to listen for mqtt topics instead of zigbee events.
Regardless, t works great for me. 
The only thing to watch out for is with double taps.
If you tap real quick, the remotes I have take it as a double tap and you have to wait about half to tap again or it won't pick up the next tap.
So, it's best to just always wait about half a second between taps if the sequence is longer than two taps. 
