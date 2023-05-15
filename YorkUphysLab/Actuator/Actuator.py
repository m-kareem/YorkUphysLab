import nidaqmx
import YorkUphysLab.GwINSTEK.GPD3303D as PSU
import time


class Actuator:
    def __init__(self, _DAQ_mame, _psu, _max_time= 12) -> None:
        self.sdaq = _DAQ_mame
        self.psu = _psu
        self.max_time = _max_time

    def set_position(self, pos, move=True):
        max_pos = 100 # mm

        if not 0 <= pos <= max_pos:
            print(f'position out of range. use 0-{max_pos} mm')
            return
        Vctrl = -0.00004*pos*pos + 0.0528*pos + 0.0481

        current_pos = self.get_position()
        required_time = abs(pos - current_pos)*self.max_time/max_pos

        if move:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(f'{self.sdaq}/ao0','mychannel',0,5)
                task.write(Vctrl)
                task.stop()
        
        time.sleep(required_time)
        print(f'position set to {pos} mm')    

    def get_position(self):
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(f'{self.sdaq}/ai0')
            Vadc = task.read()
        
        pos = 55.33223 - 31.31889*Vadc + 0.5730428*Vadc*Vadc

        return round(pos,1)

    def switch_on(self):
        self.psu.set_voltage(1, 12)
        self.psu.set_current(1, 0.4)
        self.psu.enable_output()
    
    '''
    def switch_off(self):
        self.psu.disable_output()
    '''

#==============================================================================    

# how to use this class
if __name__ == "__main__":
    
    DAQ_mame = 'SDAQ-25'
    try:
        psu = PSU.GPD3303D(port='COM8')
    except:
        print('No PSU found, or device is not connected')
        exit()
    
    if psu.is_connected():
        actuator = Actuator(DAQ_mame, psu)
        actuator.switch_on()
        actuator.set_position(10)
        print(f'position moved to = {actuator.get_position()} mm')
        
        time.sleep(2)
        psu.disable_output()
        psu.close_connection()
    else:
        print('No PSU found')
        

    '''
        SenorDAQ terminals:
        1:  p0.0
        2:  p0.1
        3:  p0.2
        4:  p0.3
        5:  GND
        6:  +5V
        7:  PFIO
        8:  GND
        9:  AO0  ----> 
        10: GND
        11: AI0  ----> 
        12: AI1
    '''