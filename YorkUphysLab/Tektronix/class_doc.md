
## Tektronix TBS1000 Oscilloscope Class Documentation

#### phase_shift(scaled_time, waveform_1, waveform_2, total_time, phase_shift)       

This member function applies a phase shift to the second waveform (`waveform_2`) based on a given phase shift value. The function takes several parameters and returns a tuple containing the time array (`scaled_time`), the original waveform 1 array (`waveform_1`), and the shifted waveform 2 array.

1. **Parameters:**
   - `scaled_time`: An array-like object representing scaled time values.
   - `waveform_1`: An array-like object representing the values of the first waveform.
   - `waveform_2`: An array-like object representing the values of the second waveform (to be phase-shifted).
   - `total_time`: A float representing the total time of the waveform.
   - `phase_shift`: A float representing the phase shift value in degrees.

2. **Calculate Phase in the Range [0, 360):**
   ```python
   _, phase = divmod(phase_shift, 360)
   ```
   The function uses `divmod` to get the quotient and remainder when `phase_shift` is divided by 360. This operation ensures that `phase` is within the range [0, 360).

3. **Calculate Period and Samples in One Period:**
   ```python
   period = self.get_period(channel=2)
   samples_in_period = int(period/total_time * len(waveform_2))
   ```
   It calls a method `get_period(channel=2)` to obtain the period of the second waveform. Then, it calculates the number of samples in one period based on the total time and the length of `waveform_2`.

4. **Calculate Shifted Samples:**
   ```python
   shift_samples = int((phase / 360) * samples_in_period)
   ```
   It calculates the number of samples to shift (`shift_samples`) in the waveform array based on the phase shift value and the number of samples in one period.

5. **Check if Shift is Needed:**
   If `shift_samples` is 0, then the function returns the original `scaled_time`, `waveform_1`, and `waveform_2` arrays.

6. **Return Shifted Arrays:**
   The function returns a tuple containing the `scaled_time`, the original `waveform_1` (not shifted), and the shifted `waveform_2`.

   Note: The function returns the shifted arrays by slicing them based on the `shift_samples` value. `[:-1*shift_samples]` in `scaled_time` and `waveform_1`, cut out the last `shift_samples` elements of the arrays, while `[shift_samples:]` in `waveform_2` cuts out the first `shift_samples` elements of the array.


   -----

#### get_data(channel)

This member function retrieves the scaled time and waveform data from the oscilloscope for the specified channel. It takes a single parameter `channel` and returns a tuple containing the following elements:
- `scaled_time`: An array of scaled time values in milliseconds.
- `scaled_wave`: An array of scaled waveform values.
- `total_time`: The total time span of the waveform in seconds.

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

9. **Create Scaled Waveform Array:**
    ```python
    unscaled_wave = np.array(bin_wave, dtype='double')  # data type conversion
    scaled_wave = (unscaled_wave - vpos) * vscale + voff
    ```
    The function creates a scaled waveform array by converting the data type of `bin_wave` to `double` and then scaling the values using the scaling factors.
    
10. **Return Data:**
    ```python
    return scaled_time, scaled_wave, total_time
    ```
    The function returns a tuple containing the scaled time array, the scaled waveform array, and the total time span of the waveform.