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
        if port:
            self.inst = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        else:
            self.inst = self.port_search(self.keyword)
    
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
        # Close serial connection
        self.inst.close()

    def read_weight_time(self):
        # Send command to scale to read weight
        self.inst.write(b'S\r\n')
        response = self.inst.readline().decode().strip()
        
        # Parse weight from response
        if response.startswith('S'):
            match = re.search(r"[-+]?\d*\.\d+|\d+", response)
            if match:
                weight = float(match.group())
        else:
            print("Error reading weight from scale")
            return

        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        return (weight, f'{hour}:{minute}:{second}')
    
    def read_weight(self):
        # Send command to scale to read weight
        self.inst.write(b'S\r\n')
        response = self.inst.readline().decode().strip()
        
        # Parse weight from response
        if response.startswith('S'):
            match = re.search(r"[-+]?\d*\.\d+|\d+", response)
            if match:
                weight = float(match.group())
        else:
            print("Error reading weight from scale")
            return

        return weight
#==============================================================================    

# how to use this class
if __name__ == "__main__":

    scale = ScoutSTX()
    #scale = ScoutSTX(port='COM7')

    wt = scale.read_weight_time()
    print(f"Weight: {wt[0]} g, at {wt[1]}")

    w = scale.read_weight()
    print(f"Weight: {w} g")
    
    # close the connection
    scale.close_connection()