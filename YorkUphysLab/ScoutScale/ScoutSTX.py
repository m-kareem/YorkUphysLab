import serial
import re
import serial.tools.list_ports
import random
import time


class ScoutSTX:
    def __init__(self, emul=False, keyword='ES', baudrate=9600, timeout=1, port=None) -> None:
        self.port = port
        self.keyword = keyword
        self.timeout = timeout
        self.baudrate = baudrate
        self.inst = None
        self.emul = emul
        self.inst_is_open = False
        if self.emul:
            self.emul_str = "[Emulation mode]:"
        else:
            self.emul_str = ""
    
    def connect(self):
        if not self.emul:
            if not self.inst_is_open:
                if self.port:
                    self.inst = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                else:
                    self.inst = self.port_search(self.keyword)

                if self.inst is not None:
                    print(f'Connected to ScoutSTX scale.')
                    self.inst_is_open = True
                    return True
                else:
                    print('ScoutSTX Connection failed.')
                    return False
            else:
                print('ScoutSTX is already connected.')
        else:
            print(f'{self.emul_str} Connected to ScoutSTX scale.')
            self.inst = 'emulated scale'
            self.inst_is_open = True
            return True
    
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
    
    def close_connection(self):
        if not self.emul:
            if self.inst is not None and self.inst.is_open:
                self.inst.close()
                print('ScoutSTX Connection closed.')
            else:
                print('No active ScoutSTX connection to close.')
        else:
            if self.inst is not None and self.inst_is_open:
                print(f'{self.emul_str} ScoutSTX Connection closed.')
        self.inst_is_open = False

    
    def is_connected(self):
        if self.inst is None:
            return False
        if self.emul:
            return self.inst_is_open
        else:
            return self.inst.is_open  
    
    def read_weight(self):
        # Send command to scale to read weight
        if self.is_connected():
            if not self.emul:
                time.sleep(1) # wait for the scale to settle
                self.inst.write(b'S\r\n')
                response = self.inst.readline().decode().strip()
                # Parse weight from response
                if response.startswith('S'):
                    match = re.search(r"[-+]?\d*\.\d+|\d+", response)
                    if match:
                        weight = float(match.group())
                    else:
                        print("Error parsing weight from scale's response")
                        return None
                else:
                    print("Error scale's response")
                    return None
            else:
                # Generate random weight
                min_value = 1.0
                max_value = 10.0
                weight = round(random.uniform(min_value, max_value), 2)
            
            return weight

        else:
            print(f'{self.emul_str} ScoutSTX Connection is not established.')
            return None

#==============================================================================    

# how to use this class
if __name__ == "__main__":
    
    scale = ScoutSTX(emul=True)
    #scale = ScoutSTX(port='COM7')
    
    # connect to the device
    scale.connect()

    wt = scale.read_weight_time()
    if wt: print(f"Weight: {wt[0]} g, at {wt[1]}")

    w = scale.read_weight()
    if w: print(f"Weight: {w} g")
    
    # close the connection
    scale.close_connection()