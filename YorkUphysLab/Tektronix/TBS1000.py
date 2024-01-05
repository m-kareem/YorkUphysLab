import pyvisa
import numpy as np
import time
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
    """
    
    def __init__(self, keyword='TBS', timeout=10000, encoding = 'latin_1', read_termination = '\n') -> None:
        self.keyword = keyword
        self.timeout = timeout
        self.encoding = encoding
        self.read_termination = read_termination
        self.write_termination = None

        self.inst = None
        self.is_open = False

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
            self.config()
            return True
        else:
            logging.info('No Tektronix TBS scope was found!')
            return False
    
    #----------------------------------------------
    def config(self):
        if self.is_connected():
            self.inst.write('*rst')  # reset the instrument to a known state.
            r = self.inst.query('*opc?')  # queries the instrument to check if it has completed the previous operation.
            self.inst.write('autoset EXECUTE')  # autoset: automatically adjusts the oscilloscope's settings based on the input signal
            r = self.inst.query('*opc?')
            self.inst.write('HORIZONTAL:MAIN:SCALE 5E-3')
            r = self.inst.query('*opc?')
            self.inst.write('CH1:COUPLING AC')
            r = self.inst.query('*opc?')
            self.inst.write('CH1:SCALE 50E-3')
            r = self.inst.query('*opc?')
            self.inst.write('CH2:SCALE 2')
            r = self.inst.query('*opc?')
            self.inst.write('TRIGGER:MAIN:EDGE:SOURCE CH2') # set trigger source to channel 2
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
    def get_data(self, channel):
        """
        Retrieves the scaled time and waveform data from the oscilloscope for the specified channel.

        Args:
            channel (int): The channel number (1 or 2) for which to retrieve the data.

        Returns:
            tuple: A tuple containing the following elements:
                - scaled_time (numpy.ndarray): An array of scaled time values in milliseconds.
                - scaled_wave (numpy.ndarray): An array of scaled waveform values.
                - total_time (float): The total time span of the waveform in seconds.
        """
        if not self.is_connected():
            return None
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1 or 2")

        scaled_wave = []
        
        """
        self.inst.write('*rst')  # reset the instrument to a known state.
        r = self.inst.query('*opc?')  # queries the instrument to check if it has completed the previous operation.
        self.inst.write('autoset EXECUTE')  # autoset: automatically adjusts the oscilloscope's settings based on the input signal
        r = self.inst.query('*opc?')
        """
        
        # io config
        self.inst.write('header 0')
        self.inst.write('data:encdg RIBINARY')
        self.inst.write(f'data:source CH{channel}')
        self.inst.write('data:start 1')  # first sample
        record = int(self.inst.query('wfmpre:nr_pt?'))  # number of samples
        self.inst.write(f'data:stop {record}')  # last sample
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

        total_time = tscale * record  # create scaled vectors
        tstop = tstart + total_time
        scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False) * 1000  # time in ms

        unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff

        return scaled_time, scaled_wave, total_time
    
    #----------------------------------------------
    def phase_shift(self, scaled_time, waveform_1, waveform_2, total_time, phase_shift):
        """
        Apply phase shift to waveform_2 based on the given phase_shift value.
        
        Parameters:
        scaled_time (array-like): Array of scaled time values.
        waveform_1 (array-like): Array of waveform 1 values.
        waveform_2 (array-like): Array of waveform 2 values.
        total_time (float): Total time of the waveform.
        phase_shift (float): Phase shift value in degrees.
        
        Returns:
        tuple: A tuple containing the shifted scaled_time, waveform_1, and shifted waveform_2.
        """
        
        _, phase = divmod(phase_shift, 360)
        # get period of waveform 2
        period = self.get_period(2)
        samples_in_period = int(period/total_time * len(waveform_2)) # number of samples in one period
        shift_samples = int((phase / 360) * samples_in_period) # number of samples to shift
        
        shifted_waveform_2 = np.roll(waveform_2, shift_samples)

        return scaled_time[shift_samples:], waveform_1[shift_samples:], shifted_waveform_2[shift_samples:]

    #----------------------------------------------
    def mix_waveforms(self, waveform_1, waveform_2):
        """
        Mixes two waveforms element-wise.

        Args:
            waveform_1 (list): The first waveform.
            waveform_2 (list): The second waveform.

        Returns:
            list: The resulting waveform after mixing.
        """
        if len(waveform_1) != len(waveform_2):
            error = f"Waveforms must be the same length: {len(waveform_1)} != {len(waveform_2)}"
            return error

        return [x*y for x,y in zip(waveform_1,waveform_2)]

#==============================================================================
# how to use this class
if __name__ == '__main__':
    # create a scope object
    scope = TBS1000()
    # connect to the scope
    scope.connect()
    
    color = {1:'orange', 2:'blue', 'mix':'red'}
    
    try:
        # retrieve waveform data
        scaled_time, scaled_wave_1, total_time = scope.get_data(channel=1)
        logging.info('ch 1 complete')
        time.sleep(3)
        scaled_time, scaled_wave_2, total_time = scope.get_data(channel=2)
        #scaled_wave_2 = np.array(scaled_wave_2)
        logging.info('ch 2 complete')
        
        phase_shift = 0
        stime, wf1,wf2 = scope.phase_shift(scaled_time, scaled_wave_1, scaled_wave_2, total_time, phase_shift)

        mix_wf = scope.mix_waveforms(wf1, wf2)
        avg_mix_wf = np.average(mix_wf)*1000 # in mV
        
        # --plotting
        #'''
        import pylab as pl
        #pl.plot(scaled_time, scaled_wave_1, label=f'Ch 1', color=color[1])
        #y_max = max(scaled_wave_1)

        #pl.plot(stime, wf1, label=f'Ch 1', color=color[1])
        #pl.plot(stime, wf2, label=f'Ch 2', color=color[2])
        pl.plot(stime, mix_wf, label=f'Mix', color=color['mix'])
        y_max = max(mix_wf)
        #y_max = max(max(wf1), max(wf2), max(mix_wf))
       
        pl.ylim(top=y_max*1.5)
        pl.xlabel('time [ms]') # x label
        pl.ylabel('voltage [v]') # y label
        # Add legend
        pl.legend(loc='upper right')
        
        pl.rc('grid', linestyle=':', color='gray', linewidth=1)
        pl.grid(True)
        pl.title(f'Lock-in Output: {round(avg_mix_wf,2)} mV,  $\Delta\phi: {phase_shift}\degree$', fontsize = 10)
        #'''
        
    except ValueError as e:
        print(e)
    

    scope.close()
    
    print("\nlook for plot window...")
    pl.show()
    print("\nend of demonstration")