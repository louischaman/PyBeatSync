import mido
from pprint import pprint

def user_midi_output(which_device_ind = None):
    midi_devices = mido.get_output_names()
    port_dict = {}
    if not which_device_ind is None:
    
        device_name = midi_devices[which_device_ind]
        inport = mido.open_output(device_name)
        port_dict[device_name] = inport
        return(port_dict)

    for i in range(len(midi_devices)):
        pprint((i, midi_devices[i]) )
    while True:
        
        user_input = raw_input('select midi device number: ')

        if user_input is "" or midi_devices is []:
            break
        try:
            which_device = int(user_input)
            device_name = midi_devices[which_device]
            inport = mido.open_output(device_name)
            port_dict[device_name] = inport
        except:
            print("please enter an into or nothing to continue")

    return(port_dict)

clock = mido.Message(type="clock")

start = mido.Message(type ="start")
stop = mido.Message(type ="stop")