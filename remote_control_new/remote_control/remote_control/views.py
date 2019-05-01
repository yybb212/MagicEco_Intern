'''
**********************************************************************
* Filename    : viewsws
* Description : views for server
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
**********************************************************************
'''

from django.shortcuts import render_to_response
from driver import camera, stream, wheels
from django.http import HttpResponse
import picar
import os

#added for LED////////////////
from pyfirmata import Arduino, util

LOW = 0
HIGH = 1

LEFT_LED = 12    #depends on which PIN a user uses
RIGHT_LED = 13  #depends on which PIN a user uses

port = '/dev/ttyACM0'
board = Arduino(port)
iterator = util.Iterator(board)
iterator.start()

board.get_pin('d:12:o')
board.get_pin('d:13:o')

#/////////////////////

#added for Vibration
#import serial
#ser = serial.Serial("/dev/ttyACM0",9600)
#/////////////////////

picar.setup()
db_file = "/home/pi/SunFounder_PiCar-V/remote_control/remote_control/driver/config"
bw = wheels.Wheels(27, 4)
fw = wheels.Wheels(17, 5)

cam = camera.Camera(debug=False, db=db_file)
cam.ready()
bw.ready()
fw.ready()

SPEED = 60
bw_status = 0

print stream.start()

def home(request):
    return render_to_response("base.html")

def run(request):

    global SPEED, bw_status
    debug = ''
    # ============== parking ===============
    if 'parking' in request.GET:
        from vibration import vibrate
        if vibrate() == True :
            return HttpResponse('Alert')
    
    # ============== linetrack ==============
    if 'linetrack' in request.GET:
        #exec(open("line_tracker.py").read())
        os.system('line_tracker.py')
        
        
    if 'action' in request.GET:
        action = request.GET['action']
    # ============== Back wheels =============
        if action == 'bwready':
            bw.ready()
            bw_status = 0
        elif action == 'forward':
            bw.speed = SPEED
            bw.clockwise()
            bw_status = 1
            debug = "speed =", SPEED
        elif action == 'backward':
            bw.speed = SPEED
            bw.counterclockwise()
            bw_status = -1
        elif action == 'stop':
            bw.stop()
            bw_status = 0
    # ============== Front wheels =============
        elif action == 'fwready':
            fw.ready()
        elif action == 'fwleft':
            board.digital[LEFT_LED].write(HIGH)
            print "LEFT HIGH is ", HIGH
            fw.speed = 100
            fw.clockwise()
        elif action == 'fwright':
            board.digital[RIGHT_LED].write(HIGH)
            print "RIGHT HIGH is ", HIGH
            fw.speed = 100
            fw.counterclockwise()
        elif action == 'fwstraight':
            fw.stop()
            board.digital[LEFT_LED].write(LOW)
            board.digital[RIGHT_LED].write(LOW)
            #while True :
            #   line = ser.readline()
            #    if len(line)>6:
            #        pass
            #    else:
             #       vib=int(line)
             #       print "Vibration : " ,vib
              #      if vib>500:
               #         print "BBIBBO BBIBBO"
               #         break
                #    else:
                 #       print "zzzzZ"
                  #      pass

        elif 'fwturn' in action:
            print "turn %s" % action
        #fw.turn(int(action.split(':')[1]))
        # ================ Camera =================
        elif action == 'camready':
            cam.ready()
        elif action == "camleft":
            cam.turn_left(40)
        elif action == 'camright':
            cam.turn_right(40)
        elif action == 'camup':
            cam.turn_up(20)
        elif action == 'camdown':
            cam.turn_down(20)

    if 'speed' in request.GET:
        speed = int(request.GET['speed'])
        SPEED = speed
        if speed < 0:
            speed = 0
        if speed > 100:
            speed = 100
            SPEED = speed
        if bw_status != 0:
            bw.speed = SPEED
            fw.speed = 100
            debug = "speed =", speed
    host = stream.get_host().split(' ')[0]
    return render_to_response("run.html", {'host': host})

def cali(request):
	if 'action' in request.GET:
		action = request.GET['action']
		# ========== Camera calibration =========
		if action == 'camcali':
			print '"%s" command received' % action
			cam.calibration()
		elif action == 'camcaliup':
			print '"%s" command received' % action
			cam.cali_up()
		elif action == 'camcalidown':
			print '"%s" command received' % action
			cam.cali_down()
		elif action == 'camcalileft':
			print '"%s" command received' % action
			cam.cali_left()
		elif action == 'camcaliright':
			print '"%s" command received' % action
			cam.cali_right()
		elif action == 'camcaliok':
			print '"%s" command received' % action
			cam.cali_ok()

		# ========= Front wheel cali ===========
		elif action == 'fwcali':
			print '"%s" command received' % action
			#fw.calibration()
		elif action == 'fwcalileft':
			print '"%s" command received' % action
			#fw.cali_left()
		elif action == 'fwcaliright':
			print '"%s" command received' % action
			#fw.cali_right()
		elif action == 'fwcaliok':
			print '"%s" command received' % action
			#fw.cali_ok()

		# ========= Back wheel cali ===========
		elif action == 'bwcali':
			print '"%s" command received' % action
			#bw.calibration()
		elif action == 'bwcalileft':
			print '"%s" command received' % action
			#bw.cali_left()
		elif action == 'bwcaliright':
			print '"%s" command received' % action
			#bw.cali_right()
		elif action == 'bwcaliok':
			print '"%s" command received' % action
			#bw.cali_ok()
		else:
			print 'command error, error command "%s" received' % action
	return render_to_response("cali.html")

def connection_test(request):
	return HttpResponse('OK')
