# Script to test spectrometer.py
import spectrometer as spect
import time
import datetime

"""
#spectrometer members:
def init()
def boardPresent()
def hwVersion()
def swVersion()
def temperatures()
def setBlueLED(state)
def shutterLED(device,state)
def setLEDDriveCurrent(current)
def setIntegrationTime(time)
def setGain(gain)
def readRAW()
def readCAL()
"""

fname = '/home/pi/python/'							# Directory for results data

def newFile(fname):

	# Open a unique file for the results data
	t = datetime.datetime.now()

	year = str(t.year)
	month = str(t.month)
	day = str(t.day)
	hour = str(t.hour)
	min = str(t.minute)

	fname = fname + 'spectrumdata' + year + month.zfill(2) + day.zfill(2) + "time" + hour.zfill(2) + 'h' + min.zfill(2) + '.txt'
	fh = open (fname,'w')

	return fh

# Test read of all calibrated and raw values
def ReadAllData():

	duration = 3600 * 20									# Desired time in secs for total run. 3600 secs per hour. 60 secs per minute.
	sleepPeriod = 60 * 10										# Sleep seconds between passes (interval between measurements)
	procTime = 6										# Board compute time per cycle (1 pass of RAW and CAL data fetch)
	passes = int(duration / (sleepPeriod + procTime))
	print ("Test duration(s): " +str(duration) + " Sleep period: " + str(sleepPeriod) + " Number of Passes: " +str(passes) )

	print ("Start time: " + str(datetime.datetime.now()))

	fhandle = newFile(fname)
	
	count = 0
	while (count < passes):
	
		print (count)

		RAWvalues = spect.readRAW()
		CALvalues = spect.readCAL()
		
		string = ""
		for val in RAWvalues:
			string = string + str(val) + ','

		for val in CALvalues:
			string = string + str(val) + ','

		string = string + "\n"
		fhandle.write(string)
		print (string)

		time.sleep(sleepPeriod)
		count = count +1

	print ("End time: " + str(datetime.datetime.now()))
	fhandle.close()





# ---- main()  -----

#spect.init()
#spect.hwVersion()
ReadAllData()


