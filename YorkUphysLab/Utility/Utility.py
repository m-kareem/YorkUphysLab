import os
import csv
import logging

from YorkUphysLab.Actuator import Actuator as ACT
from YorkUphysLab.HVcontrol import HV_control as HV
#----------------------------------------------

logging.getLogger().setLevel(logging.INFO)

def write_data_to_csv(data, path, filename):
    header = ['Position', 'Weight']
    
    # Create the full path for the CSV file on the desktop
    file_path = os.path.join(path, filename)
    
    try:
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header)
            
            for position, weight in data:
                csv_writer.writerow([position, weight])
        print(f"Data written to '{file_path}' successfully!")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
#----------------------------------------------
def reset_devices(actuator, hv):
    if not actuator.actuator_on:
        actuator.switch_on()
    actuator.set_position(0)

    if not hv.HV_on:
        hv.switch_on()
    hv.set_hv(0)

#----------------------------------------------
def multiply_lists(list_1, list_2):
    """
    Multiplies (mixes) two waveforms element-wise.
    
    Args:
        list_1 (list)
        list_2 (list)
    
    Returns:
        list: The resulting list after element-wise multiplication.
    """
    if len(list_1) != len(list_2):
        logging.error(f"Lists must be the same length: {len(list_1)} != {len(list_2)}")
        return None
    
    return [x*y for x,y in zip(list_1,list_2)]