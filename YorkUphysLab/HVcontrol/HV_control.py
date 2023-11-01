import YorkUphysLab.GwINSTEK.GPD3303D as PSU
import time


class HV_control:
    def __init__(self, _psu, emul=False) -> None:
        self.psu = _psu
        self.HV_on = False
        self.emul = emul
        if self.emul:
            self.emul_str = "[Emulation mode]:"
        else:
            self.emul_str = ""

    def switch_on(self):
        try:
            if not self.psu.is_connected():
                self.psu.connect()

            if self.psu.is_connected():
                self.psu.set_voltage(1, 12)
                self.psu.set_current(1, 0.5)
                self.psu.set_voltage(2, 1)
                self.psu.set_current(2, 0.01)
                self.psu.enable_output()
                self.HV_on = True
                message = f'{self.emul_str} HV switched ON.'
            else:
                message = f'{self.emul_str} PSU Connection is not established.'
                
        except Exception as e:
            message = f'{self.emul_str} An error occurred: {str(e)}'
        
        print(message)
        return self.HV_on
    
    def switch_off(self):
        self.psu.disable_output()
        #self.psu.close_connection()
        print(f'{self.emul_str} HV switched OFF.')
        self.HV_on = False
        return True
    
    def set_hv(self, voltage):
        if not self.HV_on:
            print(f'{self.emul_str} HV is switched OFF! Switch it ON first!')
            return None
        
        # when PSU connection is closed by another device:
        if not self.psu.is_connected():
            print("PSU Connection is not established. Switching off other devise sharing same PSU might have caused this. Switch on this decive and try again.")
            return None
        
        if 0 <= voltage <= 3:
            # Vctrl equation is a linear fit of the data below
            Vctrl = 1.6489*voltage + 0.0595
            Vctrl = 5 if Vctrl >= 5 else round(Vctrl, 1)

            #if self.HV_on:
            self.psu.set_voltage(2, Vctrl)
            print(f'{self.emul_str} HV voltage set to {voltage} kV')
            return True
            
        else:
            print(f'{self.emul_str} Requested High voltage out of range. Use 0 -3 kV')
            return None
    
    def get_hv(self):
        
        if not self.HV_on:
            print(f'{self.emul_str} HV is switched OFF! Switch it ON first!')
            return None
        
        # when PSU connection is closed by another device:
        if not self.psu.is_connected():
            print("PSU Connection is not established. Switching off other devise sharing same PSU might have caused this. Switch on this decive and try again.")
            return None
        
        # the output must be enabled to read the voltage
        actual_voltage = self.psu.get_voltage(2)
        #print(f'{self.emul_str} actual_voltage = {actual_voltage} V')
        actual_HV = (actual_voltage - 0.0595)/1.6489
        return round(actual_HV, 2)
        
#==============================================================================    

# how to use this class
if __name__ == "__main__":
        
    try:
        #psu = PSU.GPD3303D(port='COM8')
        psu = PSU.GPD3303D(emul=True)
    except:
        print('No PSU found, or device is not connected')
        exit()
    
    psu.connect()

    if psu.is_connected():
        HV = HV_control(psu, emul=True)
        
        HV.switch_on()
        HV.set_hv(1.5)
        time.sleep(2)
        actual_HV = HV.get_hv()
        print(f'Actual HV = {actual_HV} kV')
        psu.disable_output()
        psu.close_connection()
    
    else:
        print('PSU not connected')


'''
# high voltage callibration
Vctrl	V kV(cur)
0.1,	0.025127956
0.2,	0.085740858
0.3,	0.146705996
0.4,	0.207464024
0.5,	0.26828344
0.6,	0.328773566
0.7,	0.389337894
0.8,	0.449891494
1.3,	0.753993044
1.8,	1.053181468
2.3,	1.354698166
2.8,	1.654354748
3.3,	1.955916146
3.8,	2.276596628
4.3,	2.578250108
4.8,	2.875189526
'''