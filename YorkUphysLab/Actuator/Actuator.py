import nidaqmx
from YorkUphysLab.GwINSTEK import GPD3303D as PSU
import time


class Actuator:
    def __init__(self, _DAQ_mame, _psu, emul=False, _max_time= 12) -> None:
        self.sdaq = _DAQ_mame
        self.psu = _psu
        self.max_time = _max_time
        self.max_pos = 100 # mm
        self.actuator_on = False
        self.emul = emul
        self.current_pos = 0
        if self.emul:
            self.emul_str = "[Emulation mode]:"
        else:
            self.emul_str = ""

    
    def set_position(self, pos, move=True):
        
        if 0 <= pos <= self.max_pos:
            Vctrl = -0.00004*pos*pos + 0.0528*pos + 0.1
        else:
            print(f'{self.emul_str} position ({pos} mm) out of range. use 0-{self.max_pos} mm')
            return

        if self.actuator_on and move:
            self.current_pos = self.get_position()
            required_time = abs(pos - self.current_pos)*self.max_time/self.max_pos + 1
            
            if not self.emul:
                with nidaqmx.Task() as task:
                    task.ao_channels.add_ao_voltage_chan(f'{self.sdaq}/ao0','mychannel',0,5)
                    task.write(Vctrl)
                    task.stop()
        
            time.sleep(required_time)
            print(f'{self.emul_str} position set to {pos} mm')
            self.current_pos = pos    

    def get_position(self):
        if self.actuator_on:
            if not self.emul:
                with nidaqmx.Task() as task:
                    task.ai_channels.add_ai_voltage_chan(f'{self.sdaq}/ai0')
                    Vadc = task.read()
                pos = 55.33223 - 31.31889*Vadc + 0.5730428*Vadc*Vadc
            else:
                pos = self.current_pos
        else:
            print(f'{self.emul_str} Actuator is switched OFF!')
            return None
        
        return round(pos,1)

    def switch_on(self):
        try:
            if not self.psu.is_connected():
                self.psu.connect()

            if self.psu.is_connected():
                self.psu.set_voltage(1, 12)
                self.psu.set_current(1, 0.4)
                self.psu.enable_output()
                self.actuator_on = True
                message = f'{self.emul_str} Actuator switched ON.'
            else:
                message = f'{self.emul_str} PSU Connection is not established.'

        except Exception as e:
            message = f'{self.emul_str} An error occurred: {str(e)}'
        
        print(message)
        
        return self.actuator_on
    
    def switch_off(self):
        self.psu.disable_output()
        self.psu.close_connection()
        print(f'{self.emul_str} Actuator switched OFF.')
        self.actuator_on = False
        return True
#==============================================================================    

# how to use this class
if __name__ == "__main__":
    
    DAQ_mame = 'SDAQ-25'
    # create power-supply and actuator objects
    psu = PSU.GPD3303D(emul=True)
    actuator = Actuator(DAQ_mame, psu, emul=True)
    
    psu.connect()
    actuator.switch_on()
    actuator.set_position(50)
    print(f'position moved to = {actuator.get_position()} mm')
        
    time.sleep(2)
    
    actuator.switch_off()

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