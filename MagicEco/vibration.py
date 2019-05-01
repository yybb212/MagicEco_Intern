import serial
ser = serial.Serial("/dev/ttyACM3", 9600)

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)

LOW = 0
HIGH = 1

GPIO.setwarnings(False)
GPIO.setup(20, GPIO.OUT)

while True :
	line = ser.readline()
	
	if len(line) > 6 :
		pass
	
	else :
		vib = int(line)
		
		print("Vibration : ", vib)
		
		if vib > 500 :
			print("hi")
			#GPIO.output(20, HIGH)
		else :
			print("bye")
			#GPIO.output(20, LOW)
	