import GwINSTEK.GPD3303D as PSU
import time


class HV_control:
    def __init__(self, _psu) -> None:
        self.psu = _psu
    

    def switch_on(self):
        self.psu.set_voltage(1, 12)
        self.psu.set_current(1, 0.38)
        self.psu.set_voltage(2, 1)
        self.psu.set_current(2, 0.01)
        
        self.psu.enable_output()
    
    def switch_off(self):
        self.psu.disable_output()

    def set_HV_kV(self, voltage):
        if 0 <= voltage <= 3:
            # Vctrl equation is a linear fit of the data below
            Vctrl = 1.6489*voltage + 0.0595
            Vctrl = 5 if Vctrl >= 5 else round(Vctrl, 1)

            print(f'Vctrl = {Vctrl} V')
            self.psu.set_voltage(2, Vctrl)
            return True

        else:
            print('Requested High voltage out of range. Use 0 -3 kV')
            return None
    
    def get_HV_kv(self):
        # the output must be enabled to read the voltage
        actual_voltage = self.psu.get_voltage(2)
        print(f'actual_voltage = {actual_voltage} V')
        actual_HV = (actual_voltage - 0.0595)/1.6489
        return round(actual_HV, 2)

#==============================================================================    

# how to use this class
if __name__ == "__main__":

    try:
        psu = PSU.GPD3303D(port='COM8')
    except:
        print('No PSU found, or device is not connected')
        exit()

    if psu.is_connected():
        HV = HV_control(psu)
        HV.switch_on()
        HV.set_HV_kV(1.5)
        time.sleep(2)
        actual_HV = HV.get_HV_kv()
        print(f'Actual HV = {actual_HV} kV')
        HV.switch_off()
        psu.close_connection()
    
    else:
        print('No PSU found')


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