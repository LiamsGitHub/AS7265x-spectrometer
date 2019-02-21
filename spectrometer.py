# Python 2.7 module for the SparkFun Triad Spectroscopy board
# Feb 2019. Version 1


from smbus import SMBus											# Module for I2C
import time

# ---- Globals / Constants -----

I2C_ADDR =		0x49

STATUS_REG =	0x00
WRITE_REG =		0x01
READ_REG =		0x02

TX_VALID =		0x02
RX_VALID =		0x01

POLLING_DELAY = 0.05											# 50mS delay to prevent swamping the slave's I2C port
i2c = SMBus(1)													# Indicates /dev/i2c-1


# ---- Low level functions -----

# Low level function to read a Master register over I2C
# Input variables: addr (Int)
# Legal input values: n/a
# Returns: data (int)
def readReg(addr):

	status = i2c.read_byte_data(I2C_ADDR,STATUS_REG)			# Do a dummy read to ensure FIFO queue is empty
	if ((status & RX_VALID) != 0):								# There is data to be read
		incoming = i2c.read_byte_data(I2C_ADDR,READ_REG)		# Read it to clear the queue and dump it

	while (1):

		status = i2c.read_byte_data(I2C_ADDR,STATUS_REG)		# Poll Slave Status register

		if ((status & TX_VALID) == 0):							# Wait for OK to transmit
			break

		time.sleep(POLLING_DELAY)								# Polling delay to avoid drowning Slave

	i2c.write_byte_data(I2C_ADDR, WRITE_REG, addr)				# send to Write register the Virtual Register address

	while (1):
		status = i2c.read_byte_data(I2C_ADDR,STATUS_REG)		# Poll Slave Status register

		if ((status & RX_VALID) != 0):							# Wait for data to be present
			break
		time.sleep(0.05)										# Polling delay to avoid drowning Slave

	data = i2c.read_byte_data(I2C_ADDR,READ_REG)				# Finally pick up the data

	return data

# Low level function to write to a Master register over I2C
# Input variables: addr (Int), data (Int)
# Legal input values: n/a
# Returns: none
def writeReg(addr,data):

	while (1):

		status = i2c.read_byte_data(I2C_ADDR,STATUS_REG)		# Poll Slave Status register

		if ((status & TX_VALID) == 0):							# Wait for OK to transmit
			break

		time.sleep(POLLING_DELAY)

	i2c.write_byte_data(I2C_ADDR, WRITE_REG, addr | 0x80) 		# Send Virtual Register address to Write register 

	while (1):
		status = i2c.read_byte_data(I2C_ADDR,STATUS_REG)		# Poll Slave Status register

		if ((status & TX_VALID) == 0): 							# Ready for the write
			break
			
		time.sleep(POLLING_DELAY)

	i2c.write_byte_data(I2C_ADDR,WRITE_REG,data)				# Do the write
	return

# Calibrated data comes back as IEEE754 encoded number (sign/mantissa/fraction). Need to convert to a float. Spec page 27.
# Input variables: [Int] list of 4 Ints
# Legal input values: n/a
# Returns: Float
def IEEE754toFloat(valArray):

	c0 = valArray[0]
	c1 = valArray[1]
	c2 = valArray[2]
	c3 = valArray[3]
	
	fullChannel = (c0 <<24) | (c1 << 16) | (c2 << 8) | (c3)

	sign = ((1 << 31) & (fullChannel)) >> 31
	sign = (-1) ** sign

	exponent = (fullChannel >> 23) & (0xff)
	frac = fullChannel & 0x7fffff 								# filter out all but bottom 22 bits (fraction)

	accum = 1

	for bit in range(22,-1,-1):
		if (frac & (1<<bit)):
			bitfrac = 1/float(2 ** (23 - bit))
			accum = accum + bitfrac

	floatVal = sign * accum * (2 ** (exponent - 127))

	return floatVal

# Set the DEVSEL register 0X4F to point to the sensor that we want
# Input variables: (String) device name
# Legal input values: n/a
# Returns: Bool True if OK
# Note: There is a BUG in the AS firmware: you CAN'T to read/modify/write. Doesn't work. Just overwrite whole register.
def setDEVSEL(device):

	DEVSELbits = {"AS72651":0b00, "AS72652": 0b01, "AS72653": 0b10}

	try:
		mode = DEVSELbits[device]
	except:
		print ("DEVSEL bad device name")
		return (False)

	writeReg(0x4f, mode)

	return (True)
	
# Frequencies of sensors when read out serially are not in ascending order due to overlapping sensor bandwidths. Re-order data.
# Input variables: [Int] or [Float]. List of 18 data points
# Legal input values: n/a
# Returns: [Int] or [Float]. List of 18 data points
def reorderData(unsortedData):

	mappings = [(1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (8,8), (13,9), (14,11), (9,10), (10,12), (15,13), (16,14), (17,15), (18,16), (11,17), (12,18) ]
	sortedData = [0] * 18
	
	for pairs in mappings:
		sortedData[pairs[1]-1] = unsortedData[pairs[0]-1]	# -1 is to correct for 1st list member being in position 0

	return (sortedData)


# ---- Spec functions -----

# Initialize board with default settings (factory reset)
# Input variables: none
# Legal input values: none
# Returns: none
def init():

	writeReg(0x04,1)
	time.sleep(4)		# Experience was the on-board firmware needs a 2s delay after factory reset to get ready. If you poll it immediately you get [Errno 121] Remote I/O error

	return


# Return device present
# Input variables: none
# Legal input values: none
# Returns: Boolean. True, False
def boardPresent():
	try:
		device_type = readReg(0x00)
		return (True)
	except:
		return (False)

# Return system hardware version
# Input variables: void
# Legal input values:
# Returns: tuple of ints (device type, hardware version)
def hwVersion():
	device_type = readReg(0x00)
	hw_version = readReg(0x01)
	
	print (device_type, hw_version)

	return ( (device_type, hw_version) )

# Return system software version
def swVersion():
    pass

# Return current temperatures of all 3 devices in a list
# Input variables: void
# Legal input values:
# Returns: [int, int, int]
def temperatures():
	devices = ["AS72651", "AS72652", "AS72653"]
	temps = []
	for device in devices:
		setDEVSEL(device)
		temp = readReg(0x06)
		temps.append(temp)
	return (temps)


# Set master blue LED state (device 1 on IND line)
# Input variables: state (Bool)
# Legal input values: True, False
# Returns: Bool. True if OK.
def setBlueLED(state):

	setDEVSEL("AS72651")	# Blue LED attached to this device so need to select it first

	currentState = readReg(0x07)

	if (state):
		newState = (currentState | 0b1 )
	else:
		newState = (currentState & 0b11111110 )

	writeReg(0x07,newState)
	return (True)
    

# Switch on/off shutter individual LEDs attached to sensor DRV lines
# Input variables: device (String), state (Bool)
# Legal input values: device {"AS72651","AS72652","AS72653"}, state{True, False}
def shutterLED(device,state):

	DEVSELbits = {"AS72651":0b00, "AS72652": 0b01, "AS72653": 0b10}

	try:
		mode = DEVSELbits[device]
		print ("Mode = " + str(mode))
	except:
		print ("Bad device name")
		return (False)
		
	setDEVSEL(device)
	currentState = readReg(0x07)
	
	if (state == True):
		newState = (currentState | 0b1000)
	else:
		newState = (currentState & 0b11110111)
		
	writeReg(0x07,newState)
	
	return (True)


# Set LED drive current for all shutter LEDs together
# Input variables: current (Int)
# Legal input values: 0, 1, 2, 3 where b00=12.5mA; b01=25mA; b10=50mA; b11=100mA
# Returns: Bool. True if OK.
def setLEDDriveCurrent(current):

	devices = ["AS72651", "AS72652", "AS72653"]
	
	if current not in [0, 1, 2, 3]:
		print ("Illegal current setting")
		return (False)

	for device in devices:
		setDEVSEL(device)
		configReg = readReg(0x07)
		configReg = ( configReg & 0b11001111 )
		configReg = configReg | (current << 4)
		writeReg(0x07, configReg)

	return (True)


# Set integration time for all sensors together
# Input variables: time (Int)
# Legal input values: 0 to 255
# Returns: Bool. True if OK.
def setIntegrationTime(time):

	devices = ["AS72651", "AS72652", "AS72653"]
	
	if time not in range(0,255):
		print ("Illegal integration time setting")
		return (False)

	for device in devices:
		setDEVSEL(device)
		writeReg(0x05, time)
		
	for device in devices:
		setDEVSEL(device)
		print(readReg(0x05))

	return (True)


# Set sensor gains for all devices together
# Input variables: gain (Int) 
# Legal input values:  0, 1, 2, 3 where b00=1x; b01=3.7x; b10=16x; b11=64x
# Returns: Bool. True if OK.
def setGain(gain):

	devices = ["AS72651", "AS72652", "AS72653"]
	
	if gain not in [0, 1, 2, 3]:
		print ("Illegal gain setting")
		return (False)

	for device in devices:
		setDEVSEL(device)
		configReg = readReg(0x04)
		configReg = ( configReg & 0b11001111 )
		configReg = configReg | (gain << 4)
		writeReg(0x04, configReg)
		
	for device in devices:
		setDEVSEL(device)
		print(readReg(0x04))

	return (True)


# Read all 18 RAW values together
# Input variables: none
# Legal input values:  none
# Returns: [Int] list of 18 Int values
def readRAW():

	RAWRegisters = [(0x08, 0x09), (0x0a, 0x0b), (0x0c, 0x0d), (0x0e, 0x0f), (0x10, 0x11), (0x12, 0x13)]
	RAWValues = []
	devices = ["AS72651", "AS72652", "AS72653"]
	
	for device in devices:
		setDEVSEL(device)

		for regPair in RAWRegisters:
			highVal = readReg(regPair[0])
			lowVal = readReg(regPair[1])
			RAWValues.append( (highVal << 8) | (lowVal) )

# now reorder the data to be in monotonic frequency order
	output = reorderData(RAWValues)
	print output

	return (output)


# Read all 18 calibrated values together
# Input variables: none
# Legal input values:  none
# Returns: [Int] list of 18 Int values
def readCAL():

	CALRegisters = [(0x14,0x15,0x16,0x17),(0x18,0x19,0x1a,0x1b),(0x1c,0x1d,0x1e,0x1f),(0x20,0x21,0x22,0x23),(0x24,0x25,0x26,0x27),(0x28,0x29,0x2a,0x2b)]
	CALValues = []
	devices = ["AS72651", "AS72652", "AS72653"]
	
	for device in devices:
		setDEVSEL(device)

		for regQuad in CALRegisters:
			cal0 = readReg(regQuad[0])
			cal1 = readReg(regQuad[1])
			cal2 = readReg(regQuad[2])
			cal3 = readReg(regQuad[3])
			floatval = IEEE754toFloat([cal0,cal1,cal2,cal3])
			CALValues.append(floatval)

# now reorder the data to be in monotonic frequency order
	output = reorderData(CALValues)
	print output

	return (output)
