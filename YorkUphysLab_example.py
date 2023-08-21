from YorkUphysLab.ScoutScale import ScoutSTX as Scale
from YorkUphysLab.GwINSTEK import GPD3303D as PSU
from YorkUphysLab.Actuator import Actuator as ACT
from YorkUphysLab.HVcontrol import HV_control as HV

import time

# 1. Test the ScoutSTX class
scale = Scale.ScoutSTX()

if scale.is_connected():
    wt = scale.read_weight_time()
    print(f"Weight: {wt[0]} g, at {wt[1]}")

    w = scale.read_weight()
    print(f"Weight: {w} g")
    
    # close the connection
    scale.close_connection()
else:
    print('Scale not connected')

# 2. Test the GPD3303D class
psu = PSU.GPD3303D()
psu.connect()

# 3. Test the Actuator class
DAQ_mame = 'SDAQ-25' # you can find the DAQ name in the NI MAX software: Devices and Interfaces
       
actuator = ACT.Actuator(DAQ_mame, psu)
if actuator.switch_on():
    actuator.set_position(10)
    time.sleep(2)
    print(f'New position: {actuator.get_position()} mm')
    actuator.switch_off()

# 4. Test the HV_control class
hv = HV.HV_control(psu)
if hv.switch_on():
    hv.set_HV_kV(1.5)
    time.sleep(2)
    actual_HV = hv.get_HV_kv()
    print(f'Actual HV = {actual_HV} kV')
    time.sleep(5)
    hv.switch_off()