# AS7265x-spectrometer
Python module to drive the SparkFun Triad Spectroscopy Sensor

## Board physical properties

The board consists of 3 devices, each with 6 sensors with passbands ranging from UV to IR.
As can be seen from the diagram, the passbands overlap. The sensors names (A-F, G-L, R-W) and their pass frequencies are therefore somewhat jumbled, especially between the ’51 and ’52.
The 3 on-board LEDs peak at ~400nm, 475nm and 875nm. The built-in calibration should be used to optimize the sensor frequency response for the passband of interest.

![alt text](https://i.postimg.cc/T3DrFKcw/spectrum.png)

## Use

Python 2.7 for Raspberry Pi 3B

test.py instantiates the module and demonstrates use of members.

## APIs implemented

- init()
'''
Initialize board with default settings (factory reset)
Input variables: none
Legal input values: none
Returns: none
'''
- boardPresent()
'''
Return device present or not
Input variables: none
Legal input values: none
Returns: Boolean. True, False
'''
- hwVersion()
'''
Return system hardware version
Input variables: none
Legal input values: none
Returns: tuple of ints (device type, hardware version)
'''
- temperatures()
'''
Return current temperatures of all 3 devices as a list
Input variables: none
Legal input values: none
Returns: [int, int, int]
'''
- setBlueLED(state)
Set master blue LED state (device 1 on IND line)
Input variables: state (Bool)
Legal input values: True, False
Returns: Bool. True if OK.

- shutterLED(device,state)
Switch on/off shutter individual LEDs attached to sensor DRV lines
Input variables: device (String), state (Bool)
Legal input values: device {"AS72651","AS72652","AS72653"}, state{True, False}

- setLEDDriveCurrent(current)
Set LED drive current for all shutter LEDs together
Input variables: current (Int)
Legal input values: 0, 1, 2, 3 where b00=12.5mA; b01=25mA; b10=50mA; b11=100mA
Returns: Bool. True if OK.

- setIntegrationTime(time)
Set integration time for all sensors together
Input variables: time (Int)
Legal input values: 0 to 255
Returns: Bool. True if OK.

- setGain(gain)
Set sensor gains for all devices together
Input variables: gain (Int) 
Legal input values:  0, 1, 2, 3 where b00=1x; b01=3.7x; b10=16x; b11=64x
Returns: Bool. True if OK.

- readRAW()
Read all 18 RAW values together
Input variables: none
Legal input values:  none
Returns: [Int] list of 18 Int values sorted into ascending frequency order

- readCAL()
Read all 18 calibrated values together
Input variables: none
Legal input values:  none
Returns: [Int] list of 18 Int values sorted into ascending frequency order
