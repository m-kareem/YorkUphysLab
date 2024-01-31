import pyvisa
import numpy as np
import logging

#----------------------------------------------
logging.getLogger().setLevel(logging.INFO)

class TBS1000:
    """
    Represents a Tektronix TBS1000 oscilloscope.

    Attributes:
        keyword (str): The keyword used to identify the oscilloscope.
        timeout (int): The timeout value for communication with the oscilloscope.
        encoding (str): The encoding used for communication with the oscilloscope.
        read_termination (str): The read termination character for communication with the oscilloscope.
        write_termination (str): The write termination character for communication with the oscilloscope.
        inst (visa.Resource): The instrument resource representing the connected oscilloscope.
        is_open (bool): Indicates whether the oscilloscope connection is open or closed.
        total_time (flote): total time span of the waveform in seconds
    """
    
    def __init__(self, keyword='TBS', timeout=10000, encoding = 'latin_1', read_termination = '\n') -> None:
        self.keyword = keyword
        self.timeout = timeout
        self.encoding = encoding
        self.read_termination = read_termination
        self.write_termination = None

        self.inst = None
        self.is_open = False

        self.total_time = 0
        self.record = 0
        

    #----------------------------------------------
    def connect(self):
        rm = pyvisa.ResourceManager()
        resources_list = rm.list_resources()
        
        for re in resources_list:
            if 'USB' in re:
                dev = rm.open_resource(re)
                if self.keyword in dev.query('*idn?'):
                    self.inst = dev
                    break
                else:
                    dev.close()
        if self.inst:
            logging.info(f"Tektronix TBS scope found: {self.inst.query('*idn?')}")
            self.is_open = True
            self.inst.timeout = self.timeout # ms
            self.inst.encoding = self.encoding
            self.inst.read_termination = self.read_termination
            self.inst.write_termination = self.write_termination
            self.inst.write('*cls') # clear Event Status Register (ESR)
            #self.config()
            return True
        else:
            logging.info('No Tektronix TBS scope was found!')
            return False
    
    #----------------------------------------------
    def config(self, hscale='5E-3', ch1scale='50E-3', ch2scale='2', trig='CH2'):
        """
        Configures the Tektronix TBS oscilloscope with the specified settings.

        Args:
            hscale (str): Horizontal scale (time/division) setting in seconds. Default is '5E-3'.
            ch1scale (str): CH1 vertical scale (voltage/division) setting in seconds. Default is '50E-3'.
            ch2scale (str): CH2 vertical scale (voltage/division) setting in seconds. Default is '2'.
            trig (str): Trigger source setting. Default is 'CH2'. Valid options are CH1 or CH2

        Returns:
            bool: True if the oscilloscope is successfully configured, False otherwise.

        Raises:
            TypeError: If any of the arguments are not of type str.
        """
        if not all(isinstance(arg, str) for arg in (hscale, ch1scale, ch2scale, trig)):
                raise TypeError("All arguments must be of type string.")

        # Rest of the code...
        if self.is_connected():
            self.inst.write('*rst')  # reset the instrument to a known state.
            r = self.inst.query('*opc?')  # queries the instrument to check if it has completed the previous operation.
            self.inst.write('autoset EXECUTE')  # autoset: automatically adjusts the oscilloscope's settings based on the input signal
            r = self.inst.query('*opc?')
            self.inst.write(f'HORIZONTAL:MAIN:SCALE {hscale}') # set horizontal scale (time/division)
            r = self.inst.query('*opc?')
            self.inst.write('CH1:COUPLING AC')
            r = self.inst.query('*opc?')
            self.inst.write(f'CH1:SCALE {ch1scale}') # set ch1 vertical scale (voltage/division)
            r = self.inst.query('*opc?')
            self.inst.write(f'CH2:SCALE {ch2scale}') # set ch2 vertical scale (voltage/division)
            r = self.inst.query('*opc?')
            self.inst.write(f'TRIGGER:MAIN:EDGE:SOURCE {trig}') # set trigger source to channel 2
            r = self.inst.query('*opc?')
            return True
        else:
            logging.info('Tektronix TBS scope is not connected!')
            return False

    #----------------------------------------------
    def close(self):
        if self.is_connected():
            self.inst.close()
            self.is_open = False
            logging.info('Tektronix TBS scope connection is closed.')
        else:
            logging.info('Tektronix TBS scope is not connected!')

    #----------------------------------------------
    def is_connected(self):
        return self.is_open

    #----------------------------------------------
    def get_idn(self):
        if self.is_connected():
            return self.inst.query('*idn?')
        else:
            return None
    
    #----------------------------------------------
    def get_period(self, channel):
            """
            Get the period of the waveform on the specified channel.
            
            Args:
                channel (int): The channel number (1 or 2).
            Returns:
                float: The measured period in seconds.
            Raises:
                ValueError: If the channel number is not 1 or 2.
            """
            
            if channel not in [1,2]:
                raise ValueError("Channel must be 1 or 2")
            
            self.inst.write('MEASUrement:IMMed:TYPE PERiod')
            self.inst.write(f'MEASUrement:IMMed:SOUrce CH{channel}')
            measured_period = self.inst.query('MEASUrement:IMMed:VALue?')
            
            return float(measured_period) # in seconds
    
    #----------------------------------------------
    def get_frequency(self, channel):
            """
            Get the frequency of the waveform on the specified channel.
            
            Args:
                channel (int): The channel number (1 or 2).
            Returns:
                float: The measured frequency in Hz.
            Raises:
                ValueError: If the channel number is not 1 or 2.
            """
            
            if channel not in [1,2]:
                raise ValueError("Channel must be 1 or 2")
            
            self.inst.write('MEASUrement:IMMed:TYPE FREQUENCY')
            self.inst.write(f'MEASUrement:IMMed:SOUrce CH{channel}')
            measured_freq = self.inst.query('MEASUrement:IMMed:VALue?')
            
            return float(measured_freq) # in seconds

    def get_amplitude(self, channel):
            """
            Get the amplitude of the waveform on the specified channel.
            
            Args:
                channel (int): The channel number (1 or 2).
            Returns:
                float: The measured amplitude in V.
            Raises:
                ValueError: If the channel number is not 1 or 2.
            """
            
            if channel not in [1,2]:
                raise ValueError("Channel must be 1 or 2")
            
            self.inst.write('MEASUrement:IMMed:TYPE AMplitude')
            self.inst.write(f'MEASUrement:IMMed:SOUrce CH{channel}')
            measured_amplitude = self.inst.query('MEASUrement:IMMed:VALue?')
            
            return float(measured_amplitude) # in seconds
    
    def get_phase(self, channel):
            """
            Get the phase difference from the selected waveform to the designated waveform
            
            Args:
                channel (int): The channel number (1 or 2).
            Returns:
                float: The measured phase in degrees.
            Raises:
                ValueError: If the channel number is not 1 or 2.
            """
            
            if channel not in [1,2]:
                raise ValueError("Channel must be 1 or 2")
            
            self.inst.write(f'MEASUrement:IMMed:SOUrce1 CH1')
            self.inst.write(f'MEASUrement:IMMed:SOUrce2 CH2')
            self.inst.write('MEASUrement:IMMed:TYPE PHAse')
            measured_phase = self.inst.query('MEASUrement:IMMed:VALue?')
            
            if channel == 1:
                return float(measured_phase) # in degrees
            else:
                return -1*float(measured_phase) # in degrees
    #----------------------------------------------
    def get_data(self, channel):
        """
        Retrieves the waveform data from the oscilloscope for the specified channel.

        Args:
            channel (int): The channel number (1 or 2) for which to retrieve the data.

        Returns:
            A two-dimentional list(array) of the waveform containing the following elements:
            waveform[0]: An array of scaled time values in milliseconds, i.e., the x-axis values
            waveform[1]: An array of scaled amplitude values in volts, i.e., the y-axis values
        """
        if not self.is_connected():
            return None
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")
        
        # io config
        self.inst.write('header 0')
        self.inst.write('data:encdg RIBINARY')
        self.inst.write(f'data:source CH{channel}')
        self.inst.write('data:start 1')  # first sample
        self.record = int(self.inst.query('wfmpre:nr_pt?'))  # number of samples
        self.inst.write(f'data:stop {self.record}')  # last sample
        self.inst.write('wfmpre:byt_nr 1')  # 1 byte per sample
        # acq config
        self.inst.write('acquire:state 0')  # stop data acquisition
        self.inst.write('acquire:stopafter SEQUENCE')  # sets the acquisition mode to 'SEQUENCE': acquires a single waveform and then stops
        self.inst.write('acquire:state 1')  # run
        
        # data query
        bin_wave = self.inst.query_binary_values('curve?', datatype='b', container=np.array)
        tscale = float(self.inst.query('wfmpre:xincr?'))  # retrieve scaling factors
        tstart = float(self.inst.query('wfmpre:xzero?'))
        vscale = float(self.inst.query('wfmpre:ymult?'))  # volts / level
        voff = float(self.inst.query('wfmpre:yzero?'))  # reference voltage
        vpos = float(self.inst.query('wfmpre:yoff?'))  # reference position (level)
        
        # error checking
        r = int(self.inst.query('*esr?'))
        if r != 0b00000000:
            logging.info('event status register: 0b{:08b}'.format(r))
        r = self.inst.query('allev?').strip()
        if 'No events' not in r:
            logging.info(f'all event messages: {r}')

        total_time = tscale * self.record  # create scaled vectors
        tstop = tstart + total_time
        scaled_time = np.linspace(tstart, tstop, num=self.record, endpoint=False) * 1000  # time in ms

        unscaled_amp = np.array(bin_wave, dtype='double')  # data type conversion
        scaled_amp = (unscaled_amp - vpos) * vscale + voff

        self.total_time = total_time

        waveform = np.zeros((2,len(scaled_amp)))
        waveform[0] = scaled_time
        waveform[1] = scaled_amp
        
        return waveform
    
    #----------------------------------------------
    def get_data2(self):
        """
        Retrieves waveforms data of both channels of the Tektronix TBS1000 oscilloscope, simultaneously.

        Returns:
            A two-dimentional list(array) of the waveform, for each channel, containing the following elements:
            waveform[0]: An array of scaled time values in milliseconds, i.e., the x-axis values
            waveform[1]: An array of scaled amplitude values in volts, i.e., the y-axis values

            the returned values are in the following order: (waveform_1, waveform_2)
        """
        if not self.is_connected():
            return None

        scaled_amp = []

        # acq config
        self.inst.write('acquire:state RUN')  # RUN acquisition
        self.inst.write('acquire:stopafter SEQUENCE')  # sets the acquisition mode to 'SEQUENCE': acquires a single waveform and then stops
        self.inst.write('acquire:state 0')  # stop data acquisition

        # io config
        self.inst.write('header 0')
        self.inst.write('data:encdg RIBINARY')

        for channel in [1,2]:
            # ch1
            self.inst.write(f'data:source CH{channel}')
            self.inst.write('data:start 1')  # first sample
            self.record = int(self.inst.query('wfmpre:nr_pt?'))  # number of samples
            self.inst.write(f'data:stop {self.record}')  # last sample
            self.inst.write('wfmpre:byt_nr 1')  # 1 byte per sample

            # data query
            bin_wave = self.inst.query_binary_values('curve?', datatype='b', container=np.array)
            tscale = float(self.inst.query('wfmpre:xincr?'))  # retrieve scaling factors
            tstart = float(self.inst.query('wfmpre:xzero?'))
            vscale = float(self.inst.query('wfmpre:ymult?'))  # volts / level
            voff = float(self.inst.query('wfmpre:yzero?'))  # reference voltage
            vpos = float(self.inst.query('wfmpre:yoff?'))  # reference position (level)

            # error checking
            r = int(self.inst.query('*esr?'))
            if r != 0b00000000:
                logging.info('event status register: 0b{:08b}'.format(r))
            r = self.inst.query('allev?').strip()
            if 'No events' not in r:
                logging.info(f'all event messages: {r}')

            total_time = tscale * self.record  # create scaled vectors
            tstop = tstart + total_time
            scaled_time = np.linspace(tstart, tstop, num=self.record, endpoint=False) * 1000  # time in ms

            unscaled_amp = np.array(bin_wave, dtype='double')  # data type conversion
            scaled_amp.append((unscaled_amp - vpos) * vscale + voff)

            self.total_time = total_time

        waveform_1 = np.zeros((2,len(scaled_amp[0])))
        waveform_2 = np.zeros((2,len(scaled_amp[1])))
        
        
        waveform_1[0] = scaled_time
        waveform_1[1] = scaled_amp[0]
        waveform_2[0] = scaled_time
        waveform_2[1] = scaled_amp[1]

        self.inst.write('acquire:state RUN')  # RUN acquisition

        return waveform_1, waveform_2
    #----------------------------------------------
    def shift_phase(self, scaled_time, waveform_1, waveform_2, phi):
        """
        Apply phase shift to waveform_2 based on the given phi value. To keep the length of the waveforms the same, the shifted waveforms and scaled_time are truncated.
        
        Parameters:
        scaled_time (array-like): Array of scaled time values.
        waveform_1 (array-like): Array of waveform 1 values.
        waveform_2 (array-like): Array of waveform 2 values.
        phi (float): Phase shift value in degrees.
        
        Returns:
        tuple: A tuple containing the shifted scaled_time, waveform_1, and shifted waveform_2.
        """
        
        _, phase = divmod(phi, 360)    
        # get the period of waveform 2
        period = self.get_period(channel=2)
        samples_in_period = int(period/self.total_time * len(waveform_2)) # number of samples in one period
        shift_samples = int((phase / 360) * samples_in_period) # number of samples to shift

        if shift_samples == 0:
            return scaled_time, waveform_1, waveform_2
        else:
            return scaled_time[:-1*shift_samples], waveform_1[:-1*shift_samples], waveform_2[shift_samples:]
    
    #----------------------------------------------
    def shift_phase2(self, ref_waveform, ref_channel, phi_shift):
        """
        Constructing an internal reference waveform with the given phase shift w.r.t the main waveform based on the given parameters.

        Parameters:
        ref_waveform (float): The oscilloscope's readout of the rwaveform (2-dimentional list) of the reference channel
        ref_channel (str): The reference channel for obtaining the frequency
        phi_shift (float): The phase shift value in degrees.

        Returns:
        A two-dimentional list(array), with the first row element the time values and the second element being the constructed amplitude values with the shifted phase.
        """
        internal_ref_waveform = np.zeros((2,len(ref_waveform)))
        t = ref_waveform[0]
        freq = self.get_frequency(ref_channel)
        ampl = self.get_amplitude(ref_channel)
        
        # constructing a pure analytical internal ref. wave
        internal_ref_waveform[0] = t
        internal_ref_waveform[1] = ampl*np.cos(2*np.pi*freq*t*0.001 + np.radians(phi_shift))

        return internal_ref_waveform

#==============================================================================
# how to use this class
if __name__ == '__main__':
    # create a scope object
    scope = TBS1000()
    # connect to the scope
    if scope.connect():
        scope.config(hscale='5E-3', ch1scale='50E-3', ch2scale='2', trig='CH2')
    
    color = {1:'orange', 2:'blue', 'mix':'red'}
    
    #"""
    try:
        # get data from the scope
        scaled_time, scaled_wave_1, scaled_wave_2 = scope.get_data2()
        
        phi = 0
        #stime, wf1, wf2_shifted = scope.shift_phase(scaled_time, scaled_wave_1, scaled_wave_2, phi)
        wf2_shifted = scope.shift_phase2(scaled_time, ref_channel=2, phi_shift = 330)

        mix_wf = [x*y for x,y in zip(scaled_wave_1,wf2_shifted)]

        avg_mix_wf = np.average(mix_wf)*1000 # in mV
        
        # --plotting
        #'''
        import pylab as pl
        #pl.plot(scaled_time, scaled_wave_1, label=f'Ch 1', color=color[1])
        #y_max = max(scaled_wave_1)

        pl.plot(scaled_time, scaled_wave_1, label=f'Ch 1', color=color[1])
        pl.plot(scaled_time, wf2_shifted, label=f'Ch 2', color=color[2])
        #pl.plot(stime, mix_wf, label=f'Mix', color=color['mix'])
        
        y_max = max(max(scaled_wave_1), max(wf2_shifted))
        #y_max = max(max(wf1), max(wf2_shifted), max(mix_wf))
       
        pl.ylim(top=y_max*1.5)
        pl.xlabel('time [ms]') # x label
        pl.ylabel('voltage [v]') # y label
        # Add legend
        pl.legend(loc='upper right')
        
        pl.rc('grid', linestyle=':', color='gray', linewidth=1)
        pl.grid(True)
        pl.title(f'Lock-in Output: {round(avg_mix_wf,2)} mV,  $\Delta\phi: {phi}\degree$', fontsize = 10)
        #'''
        
    except ValueError as e:
        print(e)
    

    scope.close()
    
    print("\nlook for plot window...")
    pl.show()
    print("\nend of demonstration")
    
    
    scope.close()
