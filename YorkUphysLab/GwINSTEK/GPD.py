import serial
import time
import serial.tools.list_ports

class GPD3303D:
    """
    Represents the GPD3303D Programmable Power Supply Unit (PSU).

    Args:
        emul (bool): Whether to enable emulation mode. Default is False.
        keyword (str): The keyword to search for in the device identification string. Default is 'GPD'.
        baudrate (int): The baud rate for serial communication. Default is 9600.
        timeout (float): The timeout duration for serial communication in seconds. Default is 1.
        port (str): The specific port to connect to. If not provided, the port will be searched automatically.

    Attributes:
        port (str): The port used for communication.
        keyword (str): The keyword used for device identification.
        timeout (float): The timeout duration for serial communication.
        baudrate (int): The baud rate for serial communication.
        inst (serial.Serial or str): The serial connection instance or a string indicating emulation mode.
        emul (bool): Whether emulation mode is enabled.
        inst_is_open (bool): Whether the serial connection is open.
        voltage (dict): A dictionary to store the voltage values for each channel.
        current (dict): A dictionary to store the current values for each channel.
        emul_str (str): A string indicating the emulation mode.

    Methods:
        connect(): Establishes a connection to the PSU.
        port_search(keyword): Searches for the PSU on available ports.
        send_cmd(cmd): Sends a command to the PSU and returns the response.
        get_idn(): Retrieves the identification string of the PSU.
        set_voltage(channel, voltage): Sets the voltage for a specific channel.
        set_current(channel, current): Sets the current for a specific channel.
        enable_output(): Enables the output of the PSU.
        disable_output(): Disables the output of the PSU.
        enable_beep(): Enables the beep sound of the PSU.
        disable_beep(): Disables the beep sound of the PSU.
        get_voltage(channel): Retrieves the voltage value for a specific channel.
        get_current(channel): Retrieves the current value for a specific channel.
        close_connection(): Closes the connection to the PSU.
        is_connected(): Checks if the connection to the PSU is established.
    """
    def __init__(self, emul=False, keyword='GPD', baudrate=9600, timeout=1, port=None) -> None:
        self.port = port
        self.keyword = keyword
        self.timeout = timeout
        self.baudrate = baudrate
        self.inst = None
        self.emul = emul
        self.inst_is_open = False
        self.voltage ={}
        self.current ={}
        if self.emul:
            self.emul_str = "[Emulation mode]:"
        else:
            self.emul_str = ""

    def connect(self):
        if not self.emul:
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
        else:
            print(f'{self.emul_str} Connected to GPD3303D PSU.')
            self.inst = 'emulated psu'
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

    
    def send_cmd(self, cmd):
        if self.is_connected():
            self.inst.write(cmd.encode('ascii') + b'\r\n')
            resp = self.inst.readline().strip().decode('ascii')
            return resp
        else:
            print('PSU Connection is not established.')
            return None

    
    def get_idn(self):
        if self.emul:
            return 'Emulated GPD3303D PSU'
        else:
            return self.send_cmd('*IDN?')
    
    def set_voltage(self, channel, voltage):
        if not self.emul:
            cmd = f'VSET{channel}:{voltage:.1f}'
            return self.send_cmd(cmd)
        else:
            self.voltage[channel] = voltage
            return True
    
    def set_current(self, channel, current):
        if not self.emul:
            cmd = f'ISET{channel}:{current:.2f}'
            return self.send_cmd(cmd)
        else:
            self.current[channel] = current
            return True
    
    def enable_output(self):
        if not self.emul: return self.send_cmd('OUT1')
        else:
            print(f'{self.emul_str} PSU output enabled.')
            return True

    
    def disable_output(self):
        if not self.emul: return self.send_cmd('OUT0')
        else:
            print(f'{self.emul_str} PSU output disabled.')
            return True
    
    def enable_beep(self):
        if not self.emul: return self.send_cmd('BEEP1')

    def disable_beep(self):
        if not self.emul: return self.send_cmd('BEEP0')
    
    def get_voltage(self, channel):
        if not self.emul:
            response = self.send_cmd(f'VOUT{channel}?')
            if response is not None:
                voltage_str, unit_str = response.strip().split("V")
                return float(voltage_str)
        else:
            return float(self.voltage[channel])

    
    def get_current(self, channel):
        if not self.emul:
            response = self.send_cmd(f'IOUT{channel}?')
            if response is not None:
                current_str, unit_str = response.strip().split("A")
                return float(current_str)
        else:
            return float(self.current[channel])
    
    def close_connection(self):
        if not self.emul:
            if self.inst is not None and self.inst.is_open:
                self.inst.close()
                print('PSU Connection closed.')
            else:
                print('No active PSU connection to close.')
        else:
            if self.inst is not None and self.inst_is_open:
                self.inst_is_open = False
                print(f'{self.emul_str} PSU Connection closed.')
            else:
                print(f'{self.emul_str} No active PSU connection to close.')
    
    def is_connected(self):
        if self.inst is None:
            return False
        if not self.emul: return self.inst.is_open
        else: return self.inst_is_open
#==============================================================================    

# how to use this class
if __name__ == '__main__':
    # create a power-supply object
    psu = GPD3303D(emul=True)
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