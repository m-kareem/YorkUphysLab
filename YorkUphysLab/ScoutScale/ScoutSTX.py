import serial
import re
import datetime
import serial.tools.list_ports


class ScoutSTX:
    def __init__(self, keyword='ES', baudrate=9600, timeout=1, port=None) -> None:
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
            print(f'Connected to ScoutSTX scale.')
            return True
        else:
            print('ScoutSTX Connection failed.')
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
    
    def close_connection(self):
        if self.inst is not None and self.inst.is_open:
            self.inst.close()
            print('ScoutSTX Connection closed.')
        else:
            print('No active ScoutSTX connection to close.')
    
    def is_connected(self):
        if self.inst is None:
            return False
        return self.inst.is_open

    def read_weight_time(self):
        # Send command to scale to read weight
        if self.is_connected():
            self.inst.write(b'S\r\n')
            response = self.inst.readline().decode().strip()
            # Parse weight from response
            if response.startswith('S'):
                match = re.search(r"[-+]?\d*\.\d+|\d+", response)
                if match:
                    weight = float(match.group())
                    # Get current time
                    now = datetime.datetime.now()
                    hour = now.hour
                    minute = now.minute
                    second = now.second
                    
                    return (weight, f'{hour}:{minute}:{second}')
                else:
                    print("Error parsing weight from scale's response")
                    return None
            else:
                print("Error scale's response")
                return None
        else:
            print('ScoutSTX Connection is not established.')
            return None    
    
    def read_weight(self):
        # Send command to scale to read weight
        if self.is_connected():
            self.inst.write(b'S\r\n')
            response = self.inst.readline().decode().strip()
            # Parse weight from response
            if response.startswith('S'):
                match = re.search(r"[-+]?\d*\.\d+|\d+", response)
                if match:
                    weight = float(match.group())
                    return weight
                else:
                    print("Error parsing weight from scale's response")
                    return None
            else:
                print("Error scale's response")
                return None
        else:
            print('ScoutSTX Connection is not established.')
            return None 
#==============================================================================    

# how to use this class
if __name__ == "__main__":

    scale = ScoutSTX()
    #scale = ScoutSTX(port='COM7')

    # connect to the device
    scale.connect()

    wt = scale.read_weight_time()
    if wt: print(f"Weight: {wt[0]} g, at {wt[1]}")

    w = scale.read_weight()
    if w: print(f"Weight: {w} g")
    
    # close the connection
    scale.close_connection()