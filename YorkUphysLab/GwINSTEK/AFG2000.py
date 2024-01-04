import serial
import time
import serial.tools.list_ports
import logging

class AFG2000:
    
    def __init__(self, emul=False, keyword='AFG', baudrate=9600, timeout=1, port=None) -> None:
        self.port = port
        self.keyword = keyword
        self.timeout = timeout
        self.baudrate = baudrate
        self.inst = None
    #---------------------------------------------------
    
    def connect(self):
        
        if self.port:
            self.inst = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        else:
            self.inst = self.port_search(self.keyword)

        if self.inst is not None:
            print(f'Connected to {self.get_idn()}')
            return True
        else:
            print('AFG Connection failed.')
            return False
    #---------------------------------------------------

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
    #---------------------------------------------------

    def close(self):
        if self.inst is not None and self.inst.is_open:
            self.inst.close()
            print('AFG Connection closed.')
        else:
            print('No active AFG connection to close.')
    #---------------------------------------------------
    
    def is_connected(self):
        if self.inst is None:
            return False
        return self.inst.is_open
    #---------------------------------------------------
    
    def send_cmd(self, cmd):
        if self.is_connected():
            self.inst.write(cmd.encode('ascii') + b'\r\n')
            resp = self.inst.readline().strip().decode('ascii')
            return resp
        else:
            print('AFG Connection is not established.')
            return None
    #---------------------------------------------------
            
    def get_idn(self):
        return self.send_cmd('*IDN?')
    #---------------------------------------------------
    
    def set_frequency(self, freq):
        if self.is_connected():
            self.send_cmd(f'SOUR1:FREQ {freq}')
            return True
        else:
            logging.info('AFG2000 function generator is not connected!')
            return False
	#---------------------------------------------------
	
    def set_waveform(self, waveform='SIN'):
        if self.is_connected():
            if waveform in ['SIN', 'SQU', 'RAMP', 'NOIS', 'ARB']:
                self.send_cmd(f'SOUR1:FUNC {waveform}')
                return True
            else:
                logging.error(f'Invalid waveform: {waveform}. Valid waveforms are "SIN", "SQU", "RAMP", "NOIS", and "ARB".')
                return None
        else:
            logging.info('AFG2000 function generator is not connected!')
            return False
	#---------------------------------------------------
        
    def set_amplitude(self, amplitude, unit='VPP'):
        if self.is_connected():
            if unit in ['VPP', 'VRMS', 'DBM']:
                self.send_cmd(f'SOUR1:VOLT:UNIT {unit}')
            else:
                logging.error(f'Invalid unit: {unit}. Valid units are "VPP", "VRMS", and "DBM".')
                return None
            self.send_cmd(f'SOUR1:AMPL {amplitude}')
            return True
        else:
            logging.info('AFG2000 function generator is not connected!')
            return False
    #---------------------------------------------------
        
    def set_DCoffset(self, offset):
        if self.is_connected():
            self.send_cmd(f'SOUR1:DCO {offset}')
            return True
        else:
            logging.info('AFG2000 function generator is not connected!')
            return False
    #---------------------------------------------------
        
    def set_output(self, state):
        if self.is_connected():
            if state in ['ON', 'OFF']:
                self.send_cmd(f'OUTP {state}')
                return True
            else:
                logging.error(f'Invalid output state: {state}. Valid states are "ON" and "OFF".')
                return None
        else:
            logging.info('AFG2000 function generator is not connected!')
            return False
#==============================================================================    

# how to use this class
if __name__ == '__main__':
    afg = AFG2000()
    afg.connect()
    afg.set_waveform('SIN')
    afg.set_frequency('70')
    afg.set_amplitude('0.2', 'VPP')
    afg.set_DCoffset('0.0')
    afg.set_output('ON')
    time.sleep(10)

    afg.set_amplitude('0.35')
    afg.set_frequency('90')
    time.sleep(10)
    afg.set_output('OFF')
    afg.close()