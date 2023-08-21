import serial
import time
import serial.tools.list_ports

class GPD3303D:
    def __init__(self, keyword='GPD', baudrate=9600, timeout=1, port=None) -> None:
        self.port = port
        self.keyword = keyword
        self.timeout = timeout
        self.baudrate = baudrate
        self.inst = None

    def connect(self):
        if self.port:
            self.inst = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        else:
            self.inst = self.port_search(self.keyword)
        
        if self.inst is not None:
            print(f'Connected to {self.get_idn()}')
            return True
        else:
            print('PSU Connection failed.')
            return False

    def port_search(self, keyword):
        print('Searching for the device...')
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            ser = serial.Serial(port, self.baudrate, timeout=self.timeout)
            ser.write(b'*IDN?\r\n')
            idn = ser.readline().strip().decode('ascii')
            
            if keyword in idn:
                print(f'"{keyword}" found in: {port}')
                return ser
            else:
                ser.close()
            
        print(f'"{keyword}" is not found on any port')
        return None

    
    def send_cmd(self, cmd):
        if self.is_connected():
            self.inst.write(cmd.encode('ascii') + b'\r\n')
            resp = self.inst.readline().strip().decode('ascii')
            return resp
        else:
            print('PSU Connection is not established.')
            return None

    
    def get_idn(self):
        return self.send_cmd('*IDN?')
    
    def set_voltage(self, channel, voltage):
        cmd = f'VSET{channel}:{voltage:.1f}'
        return self.send_cmd(cmd)
    
    def set_current(self, channel, current):
        cmd = f'ISET{channel}:{current:.2f}'
        return self.send_cmd(cmd)
    
    def enable_output(self):
        return self.send_cmd('OUT1')
    
    def disable_output(self):
        return self.send_cmd('OUT0')
    
    def enable_beep(self):
        return self.send_cmd('BEEP1')

    def disable_beep(self):
        return self.send_cmd('BEEP0')
    
    def get_voltage(self, channel):
        response = self.send_cmd(f'VOUT{channel}?')
        if response is not None:
            voltage_str, unit_str = response.strip().split("V")
            return float(voltage_str)
    
    def get_current(self, channel):
        response = self.send_cmd(f'IOUT{channel}?')
        if response is not None:
            current_str, unit_str = response.strip().split("A")
            return float(current_str)
    
    def close_connection(self):
        if self.inst is not None and self.inst.is_open:
            self.inst.close()
            print('PSU Connection closed.')
        else:
            print('No active PSU connection to close.')
    
    def is_connected(self):
        if self.inst is None:
            return False
        return self.inst.is_open 
    
#==============================================================================    

# how to use this class
if __name__ == '__main__':
    # create a power-supply object
    psu = GPD3303D()
    #psu = GPD3303D(port='COM8')

    # connect to the device
    psu.connect()

    # Set the output voltage and current for channel 1
    psu.set_voltage(1, 12)
    psu.set_current(1, 0.01)

    # Set the output voltage and current for channel 2
    psu.set_voltage(2, 4.7)
    psu.set_current(2, 0.05)
    
    # Enable the output
    psu.enable_output()

    time.sleep(2)
    #print(f'voltage - CH1: {psu.get_voltage(1)} V')
    #print(f'current - CH1: {psu.get_current(1)} A')
    print(f'voltage - CH2: {psu.get_voltage(2)} V')
    #print(f'current - CH2: {psu.get_current(2)} A')
    
    # Disable the output
    psu.disable_output()

    # close the connection
    psu.close_connection()