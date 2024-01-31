
## Tektronix TBS1000 Oscilloscope Class Documentation
=======================================================================

#### get_data(channel)

This member function retrieves the waveform data from the oscilloscope for the specified channel. It takes a single parameter `channel` and returns a two-dimentional list(array) of the waveform containing the following elements:
- `scaled_time`: An array of scaled time values in milliseconds, i.e., the x-axis values
- `scaled_amplitude`: An array of scaled waveform values, i.e., the y-axis values

1. **Check Connection:**
   ```python
   if not self.is_connected():
      return None
   ```
   The function checks if the oscilloscope is connected. If not, it returns `None`.

2. **Check Channel:**
   ```python
    if channel not in [1, 2]:
        raise ValueError("Channel must be 1 or 2")
    ```
    The function checks if the channel number is valid. If not, it raises a `ValueError`.

3. **Configure I/O:**
    ```python
    self.inst.write('header 0')
    self.inst.write('data:encdg RIBINARY')
    self.inst.write(f'data:source CH{channel}')
    self.inst.write('data:start 1')  # first sample
    record = int(self.inst.query('wfmpre:nr_pt?'))  # number of samples
    self.inst.write(f'data:stop {record}')  # last sample
    self.inst.write('wfmpre:byt_nr 1')  # 1 byte per sample
    ```
    The function configures the I/O settings of the oscilloscope to retrieve the waveform data from the specified channel. It sets the header to 0, the data encoding to RIBINARY, the data source to the specified channel, the first sample to 1, the last sample to the total number of samples, and the number of bytes per sample to 1.

4. **Configure Acquisition:**
    ```python   
    # acq config
    self.inst.write('acquire:state 0')  # stop data acquisition
    self.inst.write('acquire:stopafter SEQUENCE')  # sets the acquisition mode to 'SEQUENCE': acquires a single waveform and then stops
    self.inst.write('acquire:state 1')  # run
    ```
    The function configures the acquisition settings of the oscilloscope to acquire a single waveform and then stop.

5. **Query Data:**
    ```python
    bin_wave = self.inst.query_binary_values('curve?', datatype='b', container=np.array)
    tscale = float(self.inst.query('wfmpre:xincr?'))  # retrieve scaling factors
    tstart = float(self.inst.query('wfmpre:xzero?'))
    vscale = float(self.inst.query('wfmpre:ymult?'))  # volts / level
    voff = float(self.inst.query('wfmpre:yzero?'))  # reference voltage
    vpos = float(self.inst.query('wfmpre:yoff?'))  # reference position (level)
    ```
    The function queries the oscilloscope for the waveform data and scaling factors. It queries the waveform data using the `curve?` command and the scaling factors using the `wfmpre:xincr?`, `wfmpre:xzero?`, `wfmpre:ymult?`, `wfmpre:yzero?`, and `wfmpre:yoff?` commands.

6. **Check for Errors:**
    ```python
    # error checking
    r = int(self.inst.query('*esr?'))
    if r != 0b00000000:
        logging.info('event status register: 0b{:08b}'.format(r))
    r = self.inst.query('allev?').strip()
    if 'No events' not in r:
        logging.info(f'all event messages: {r}')
    ```
    The function checks for errors by querying the event status register and the event messages. If there are errors, it logs the event status register and the event messages.

7. **Calculate Total Time:**
    ```python
    total_time = tscale * record  # create scaled vectors
    ```
    The function calculates the total time span of the waveform in seconds by multiplying the time scale by the number of samples.
    
8. **Create Scaled Time Array:**
    ```python
    tstop = tstart + total_time
    scaled_time = np.linspace(tstart, tstop, num=record, endpoint=False) * 1000  # time in ms
    ```
    The function creates a scaled time array by using the `np.linspace()` function to create an array of evenly spaced numbers between `tstart` and `tstop` with `record` number of elements. It then multiplies the array by 1000 to convert the time values from seconds to milliseconds.

9. **Create Scaled Amplitude Array:**
    ```python
    unscaled_amp = np.array(bin_wave, dtype='double')  # data type conversion
    scaled_amp = (unscaled_amp - vpos) * vscale + voff
    ```
    The function creates a scaled amplitude array by converting the data type of `bin_wave` to `double` and then scaling the values using the scaling factors.
    
10. **Return Data:**
    ```python
    waveform = np.zeros((2,len(scaled_amp)))
    waveform[0] = scaled_time
    waveform[1] = scaled_amp
        
    return waveform
    ```
    The function returns a two-dimensional list containing the scaled time array and the scaled amplitude array, i.e., the waveform data.

=======================================================================

#### get_data2()
This member function retrieves waveforms data of both channels of the oscilloscope. It returns a two-dimentional list(array) of the waveform, for each channel, containing the following elements:
- `scaled_time`: An array of scaled time values in milliseconds for channel 1 (x-axis values)
- `scaled_amplitude`: An array of scaled amplitude values for channel 1 (y-axis values)

The returned values are in the following order: (waveform_1, waveform_2).

The function follows the same steps as the `get_data(channel)` function for each channel and returns the waveforms for both channels sequentially. Note that the function reads the waveform data from both channels simultaneously by freezing the acquisition and querying the waveform data for each channel individually.

=======================================================================

#### phase_shift2(ref_waveform, ref_channel, phi_shift)       

This member function applies a phase shift to the reference waveform (`ref_waveform`) based on a given phase shift value. The function takes several parameters and returns a two-dimensional waveform containing the time array (`scaled_time`) and the amplitude of the constructed pure internal reference

1. **Parameters:**
   - `ref_waveform`: A two-diemnsion array object representing the reference waveform.
   - `ref_channel`: The reference channel number for obtaining the frequency, i.e., 1 or 2.
   - `phi`: A float number representing the target phase shift in degrees.

2. **Creating an empty two-dimensional array of the output:**
   ```python
   internal_ref_waveform = np.zeros((2,len(ref_waveform)))
   ```
   

3. **Obtaining the frequency from the Oscillosope:**
   ```python
   freq = self.get_frequency(ref_channel)
   ```
   It calls a method `get_frequency(ref_channel)` to obtain the frequency of the reference channel.

4. **Constructing the internal pure (analytical) reference waveform:**
   ```python
    internal_ref_waveform[0] = t
    internal_ref_waveform[1] = np.cos(2*np.pi*freq*t*0.001 + np.radians(phi_shift))
   ```
   It assigns the time array part of the reference waveform as the first dimension of the `internal_ref_waveform` array. 
   The second dimension is assigned analytically as: `A*Cos(2*pi*freq*t + phi)`, where A is the amplitude, freq is the frequency, t is the time array, and phi is the phase shift in radians.
   
   Finally, it returns the constructed two-dimensional internal reference waveform.

=======================================================================