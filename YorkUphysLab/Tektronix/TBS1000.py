import visa # http://github.com/hgrecco/pyvisa
import numpy as np
import time
class TBS1000:
    """
    A class representing representing the Tektronix TBS1000 oscilloscope.

    Attributes:
        keyword (str): The keyword used to identify the oscilloscope. Defaults to 'TBS'.
        timeout (int): The timeout value in milliseconds. Defaults to 10000.
        encoding (str): The encoding used for communication. Defaults to 'latin_1'.
        read_termination (str): The read termination character. Defaults to '\n'.

    Methods:
        connect(): Connects to the oscilloscope.
        close(): Closes the connection to the oscilloscope.
        is_connected(): Checks if the oscilloscope is connected.
        get_idn(): Retrieves the identification string of the oscilloscope.
        get_data(channel=1): Retrieves waveform data from the oscilloscope.

    Note:
        - The oscilloscope must be connected before calling any other methods.
        - The oscilloscope settings are automatically adjusted based on the input signal.
        - The waveform data is retrieved in binary format.
        - The scaling factors for time and voltage are retrieved from the oscilloscope.
        - Error checking is performed to ensure the data acquisition is successful.
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
        rm = visa.ResourceManager()
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
            print(f"Tektronix TBS scope found: {self.inst.query('*idn?')}")
            self.is_open = True
            self.inst.timeout = self.timeout # ms
            self.inst.encoding = self.encoding
            self.inst.read_termination = self.read_termination
            self.inst.write_termination = self.write_termination
            self.inst.write('*cls') # clear Event Status Register (ESR)
            return True
        else:
            print('No Tektronix TBS scope was found!')
            return False
    #----------------------------------------------
    def close(self):
        if self.is_connected():
            self.inst.close()
            self.is_open = False
            print('Tektronix TBS scope connection is closed.')
        else:
            print('Tektronix TBS scope is not connected!')

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
        if channel not in [1,2]:
            raise ValueError("Channel must be 1 or 2")
        self.inst.write('MEASUrement:IMMed:TYPE PERiod')
        self.inst.write(f'MEASUrement:IMMed:SOUrce CH{channel}')
        measured_period = self.inst.query('MEASUrement:IMMed:VALue?')
        
        return float(measured_period) # in seconds
    
    #----------------------------------------------
    def get_data(self, channel):
        """
        Retrieves the waveform data from the Tektronix TBS1000 oscilloscope.

        Args:
            channel (int or str): The channel number or channel name. Defaults to 1.
                - If 'multi', retrieves data from both channels.
                - If 'diff', retrieves the differential data between channels 1 and 2.
                - If 1 or 2, retrieves data from the specified channel.

        Returns:
            tuple: A tuple containing the scaled time values and the scaled waveform data.
                - The scaled time values are in milliseconds.
                - The scaled waveform data is a list of numpy arrays.

        Raises:
            ValueError: If the channel argument is invalid.

        Note:
            - The oscilloscope must be connected before calling this method.
            - The oscilloscope settings are automatically adjusted based on the input signal.
            - The waveform data is retrieved in binary format.
            - The scaling factors for time and voltage are retrieved from the oscilloscope.
            - Error checking is performed to ensure the data acquisition is successful.
        """
        if not self.is_connected():
            return None
        if channel not in [1, 2]:
            raise ValueError("Channel must be 1, or 2")

        scaled_wave = []

        self.inst.write('*rst')  # reset the instrument to a known state.
        r = self.inst.query('*opc?')  # queries the instrument to check if it has completed the previous operation.
        self.inst.write('autoset EXECUTE')  # autoset: automatically adjusts the oscilloscope's settings based on the input signal
        r = self.inst.query('*opc?')
        # io config
        self.inst.write('header 0')
        self.inst.write('data:encdg RIBINARY')
        self.inst.write(f'data:source CH{channel}')  # channel
        self.inst.write('data:start 1')  # first sample
        record = int(self.inst.query('wfmpre:nr_pt?'))  # number of samples
        self.inst.write(f'data:stop {record}')  # last sample
        self.inst.write('wfmpre:byt_nr 1')  # 1 byte per sample
        # acq config
        self.inst.write('acquire:state 0')  # stop data acquisition
        self.inst.write('acquire:stopafter SEQUENCE')  # sets the acquisition mode to 'SEQUENCE': acquires a single waveform and then stops
        self.inst.write('acquire:state 1')  # run
        r = self.inst.query('*opc?')  # sync
        bin_wave = self.inst.query_binary_values('curve?', datatype='b', container=np.array)
        tscale = float(self.inst.query('wfmpre:xincr?'))  # retrieve scaling factors
        tstart = float(self.inst.query('wfmpre:xzero?'))
        vscale = float(self.inst.query('wfmpre:ymult?'))  # volts / level
        voff = float(self.inst.query('wfmpre:yzero?'))  # reference voltage
        vpos = float(self.inst.query('wfmpre:yoff?'))  # reference position (level)
        r = int(self.inst.query('*esr?'))  # error checking
        if r != 0b00000000:
            print('event status register: 0b{:08b}'.format(r))
        r = self.inst.query('allev?').strip()
        if 'No events' not in r:
            print('all event messages: {}'.format(r))
        
        total_time = tscale * record  # create scaled vectors
        tstop = tstart + total_time
        scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False) * 1000  # time in ms
        
        unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
        scaled_wave = (unscaled_wave - vpos) * vscale + voff
                   
        return scaled_time, scaled_wave, total_time
    
    
    #----------------------------------------------
    def phase_shift(self, scaled_time, waveform_1, waveform_2, total_time, phase_shift):
        _, phase = divmod(phase_shift, 360)
        # get period of waveform 2
        period = self.get_period(2)

        samples_in_period = int(period/total_time * len(waveform_2)) # number of samples in one period (samples

        shift_samples = int((phase / 360) * samples_in_period) # number of samples to shift
        
        #print(f"phase shift: {phase} deg, shift_samples: {shift_samples}, total samples: {len(waveform_2)}")
        
        shifted_waveform_2 = np.roll(waveform_2, shift_samples)

        return scaled_time[shift_samples:], waveform_1[shift_samples:], shifted_waveform_2[shift_samples:]

    def mix_waveforms(self, waveform_1, waveform_2):
        if len(waveform_1) != len(waveform_2):
            error = f"Waveforms must be the same length: {len(waveform_1)} != {len(waveform_2)}"
            return error
        
        return [x*y for x,y in zip(waveform_1,waveform_2)]
#----------------------------------------------
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
        print('ch 1 complete')
        time.sleep(12)
        scaled_time, scaled_wave_2, total_time = scope.get_data(channel=2)
        print('ch 2 complete')
        
        phase_shift = 30
        stime, wf1,wf2 = scope.phase_shift(scaled_time, scaled_wave_1, scaled_wave_2, total_time, phase_shift)

        mix_wf = scope.mix_waveforms(wf1, wf2)
        avg_mix_wf = np.average(mix_wf)
        
        # --plotting
        #'''
        import pylab as pl
        pl.plot(stime, wf1, label=f'Ch 1, 100Hz', color=color[1])
        pl.plot(stime, wf2, label=f'Ch 2, 70 Hz', color=color[2])
        pl.plot(stime, mix_wf, label=f'Mix', color=color['mix'])
        y_max = max(max(wf1), max(wf2), max(mix_wf))
       
        pl.ylim(top=y_max*1.5)
        pl.xlabel('time [ms]') # x label
        pl.ylabel('voltage [v]') # y label
        # Add legend
        pl.legend(loc='upper right')
        
        pl.rc('grid', linestyle=':', color='gray', linewidth=1)
        pl.grid(True)
        pl.title(f'avg_mix_wf: {round(avg_mix_wf,2)}, d_phi: {phase_shift}', fontsize = 14)
        #'''
        
    except ValueError as e:
        print(e)
    

    scope.close()
    
    #"""
    print("\nlook for plot window...")
    pl.show()
    print("\nend of demonstration")
    #"""