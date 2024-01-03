import pyvisa
import time
import logging

#---------------------------------------------------

logging.getLogger().setLevel(logging.INFO)

class AFG2000:
	"""
	A class representing the AFG2000 function generator.

	Attributes:
		keyword (str): The keyword used to identify the AFG2000 device.
		timeout (int): The timeout value for communication with the device.
		inst (visa.Resource): The resource object representing the connected AFG2000 device.
		is_open (bool): Flag indicating whether the device is connected or not.

	Methods:
		connect(): Connects to the AFG2000 device.
		close(): Closes the connection to the AFG2000 device.
		is_connected(): Checks if the AFG2000 device is connected.
		get_idn(): Retrieves the identification string of the AFG2000 device.
		set_frequency(freq): Sets the frequency of the waveform output.
		set_waveform(waveform): Sets the waveform type of the output signal.
		set_amplitude(amplitude, unit): Sets the amplitude of the output signal.
		set_DCoffset(offset): Sets the DC offset of the output signal.
		set_output(state): Sets the output state of the AFG2000 device.
	"""
	def __init__(self, keyword='AFG', timeout=5000) -> None:
		self.keyword = keyword
		self.timeout = timeout
		self.inst = None
		self.is_open = False

    
	def connect(self):
		rm = pyvisa.ResourceManager()
		resources_list = rm.list_resources()
		
		for re in resources_list:
			if 'INSTR' in re:
				dev = rm.open_resource(re)
				if self.keyword in dev.query('*idn?'):
					self.inst = dev
					break
				else:
					dev.close()
		if self.inst:
			logging.info(f"AFG2000 function generator found: {self.inst.query('*idn?')}")
			self.is_open = True
			self.inst.timeout = self.timeout # ms
			return True
		else:
			logging.info('No AFG2000 function generator was found!')
			return False
	
	def close(self):
		if self.is_connected():
			self.inst.close()
			self.is_open = False
			logging.info('AFG2000 function generator connection is closed.')
			return True
		else:
			logging.info('AFG2000 function generator is not connected!')
			return False
	
	def is_connected(self):
		return self.is_open
	
	def get_idn(self):
		if self.is_connected():
			return self.inst.query('*idn?')
		else:
			logging.info('AFG2000 function generator is not connected!')
			return False
		
	def set_frequency(self, freq):
		if self.is_connected():
			self.inst.write(f'SOUR1:FREQ {freq}')
			return True
		else:
			logging.info('AFG2000 function generator is not connected!')
			return False
	
	
	def set_waveform(self, waveform='SIN'):
		if self.is_connected():
			if waveform in ['SIN', 'SQU', 'RAMP', 'NOIS', 'ARB']:
				self.inst.write(f'SOUR1:FUNC {waveform}')
				return True
			else:
				logging.error(f'Invalid waveform: {waveform}. Valid waveforms are "SIN", "SQU", "RAMP", "NOIS", and "ARB".')
				return None
		else:
			logging.info('AFG2000 function generator is not connected!')

			return False
	
	def set_amplitude(self, amplitude, unit='VPP'):
		if self.is_connected():
			if unit in ['VPP', 'VRMS', 'DBM']:
				self.inst.write(f'SOUR1:VOLT:UNIT {unit}')
			else:
				logging.error(f'Invalid unit: {unit}. Valid units are "VPP", "VRMS", and "DBM".')
				return None
			self.inst.write(f'SOUR1:AMPL {amplitude}')
			return True
		else:
			logging.info('AFG2000 function generator is not connected!')
			return False

	def set_DCoffset(self, offset):
		if self.is_connected():
			self.inst.write(f'SOUR1:DCO {offset}')
			return True
		else:
			logging.info('AFG2000 function generator is not connected!')
			return False

	def set_output(self, state):
		if self.is_connected():
			if state in ['ON', 'OFF']:
				self.inst.write(f'OUTP {state}')
				return True
			else:
				logging.error(f'Invalid output state: {state}. Valid states are "ON" and "OFF".')
				return None
		else:
			logging.info('AFG2000 function generator is not connected!')
			return False
		

#---------------------------------------------------
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

	afg.set_amplitude('0.25')
	time.sleep(10)
	afg.set_output('OFF')
	afg.close()
	
	


