#*********************************libraries***************************************
import sys
sys.path.insert(0, "/home/pi/remote_control_new/remote_control/remote_control")
from picar.SunFounder_PCA9685 import Servo
import picar
from time import sleep
import cv2
import cv2.cv as cv
import numpy as np
from driver import camera, stream, wheels
#*********************************************************************************

picar.setup()
# Show image captured by camera, True to turn on, you will need #DISPLAY and it also slows the speed of tracking
show_image_enable   = False
draw_circle_enable  = False
scan_enable         = True
rear_wheels_enable  = True
front_wheels_enable = True
pan_enable          = True


kernel = np.ones((5,5),np.uint8)
img = cv2.VideoCapture(-1)  # choose a video

SCREEN_WIDTH = 160  # Screen width
SCREEN_HEIGHT = 120  # Screen Hight
img.set(3,SCREEN_WIDTH)
img.set(4,SCREEN_HEIGHT)
CENTER_X = SCREEN_WIDTH/2
CENTER_Y = SCREEN_HEIGHT/2

# Camera setting
CAMERA_STEP = 2
CAMERA_X_ANGLE = 80
CAMERA_Y_ANGLE = 80

# motor set
adjusted_angle      = 50
PAN_ANGLE_MAX   = 170
PAN_ANGLE_MIN   = 10
TILT_ANGLE_MAX  = 90
TILT_ANGLE_MIN  = 20
FW_ANGLE_MAX    = adjusted_angle+50
FW_ANGLE_MIN    = adjusted_angle-50

SCAN_POS = [50, 70, 90, 110, 130, 130, 110, 90, 70, 50]

bw = wheels.Wheels(27, 4)
fw = wheels.Wheels(17, 5)
pan_servo = Servo.Servo(1)
tilt_servo = Servo.Servo(2)
picar.setup()

fw.offset = 0
pan_servo.offset = 10
tilt_servo.offset = 0

bw.speed = 0
#fw.turn(adjusted_angle)
pan_servo.write(90)
tilt_servo.write(60)
cx = 0
cy = 0

motor_speed = 40

def nothing(x):
    pass

def main():
    pan_angle = 90              # initial angle for pan
    tilt_angle = 60             # initial angle for tilt
    fw_angle = adjusted_angle   # initial angle for forward angle

    print("Begin!")
    scan_count = 0

    while True:
        x = 0             # x initial in the middle
        y = 0             # y initial in the middle

        # Find the center of contour
        for i in range(10):
            (x, y) = find_blob(x, y)

    # If the road is not found, False
        if x == 0 and y == 0 :
            isFound = False
        else :
            isFound = True
            scan_count = 0

    # Stop the car and Detect line
        if isFound == False :
            print("scanning...")
            bw.stop()

            if scan_enable:
                pan_angle = SCAN_POS[scan_count]

            if pan_enable:
                pan_servo.write(pan_angle)
            bw.speed=motor_speed+40
            bw.counterclockwise()
            print("when backing, fw_angle is ",fw_angle)
            if fw_angle< 50 :
                fw.speed=100
                fw.counterclockwise()
            else:
                fw.speed=100
                fw.clockwise()


            scan_count += 1


            # Finish driving after scanning
            if scan_count >= len(SCAN_POS):

                print "End driving!"
                fw.stop()
                bw.stop()
                break

            else:
                sleep(0.1)

            # Car follows the road
        else :
            delta_x = CENTER_X - x
            delta_y = CENTER_Y - y

            print "x = %s, delta_x = %s" % (x, delta_x)
            print "y = %s, delta_y = %s" % (y, delta_y)

            # Degree for x-axis
            delta_angle = int(float(CAMERA_X_ANGLE) / SCREEN_WIDTH * delta_x)
            print "delta_pan = %s" % delta_angle
            fw_angle = adjusted_angle - delta_angle

            if fw_angle > FW_ANGLE_MAX:
                fw_angle = FW_ANGLE_MAX
            elif fw_angle < FW_ANGLE_MIN:
                fw_angle = FW_ANGLE_MIN


# Normal range
            if FW_ANGLE_MIN < fw_angle and fw_angle < FW_ANGLE_MAX:
                print("1 and fw_angle is ",fw_angle)
                if front_wheels_enable:
                    scan_count = 0
                    if fw_angle > 50 :
                        fw.speed = 100
                        fw.counterclockwise()#right
                        print("2")
                    else :
                        fw.speed = 100
                        fw.clockwise()#left
                        print("3")

                if rear_wheels_enable:
                    print("4")
                    bw.speed = motor_speed
                    bw.clockwise()

                # Out of range
            else:
                bw.stop()
                fw_angle = (adjusted_angle - fw_angle) + adjusted_angle
                print("5")
                if front_wheels_enable:
                    if fw_angle > 50 :
                        fw.speed = 100
                        fw.counterclockwise()
                        print("6")
                    else :
                        fw.speed = 100
                        fw.clockwise()
                        print("7")

                if rear_wheels_enable:
                    print("8")
                    bw.speed = motor_speed - 5
                    bw.counterclockwise()

def destroy():
    bw.stop()
    img.release()

def test():
    fw.turn(90)

def find_blob(prior_x, prior_y) :

    # Load input image
    _, bgr_image = img.read()

    # Crop the image
    crop_image = bgr_image[60:240, 0:160]

    # Convert to grayscale
    gray = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)

    # Converts images from BGR to HSV
    hsv = cv2.cvtColor(crop_image, cv2.COLOR_BGR2HSV)

    # Set blue color range
    lower_blue = np.array([110, 50, 50])
    upper_blue = np.array([130, 255, 255])

    '''
    lower_red = np.array([160, 20, 70])
    upper_red - np.array([190, 255, 255])
    '''

    #find the colors within the specified boundaries and apply
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Remain only blue color area
    res = cv2.bitwise_and(crop_image, crop_image, mask = mask)

    # Color thresholding
    ret, thresh = cv2.threshold(mask, 60, 255, cv2.THRESH_BINARY_INV)

    # Find the contours of the frame
    contours, hierarchy = cv2.findContours(mask, 1, cv2.CHAIN_APPROX_NONE)

    # Find the biggest contour (if detected)
    if len(contours) > 0:

        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        # No exist contour, Use the prior coordinate
        if M['m00'] == 0.0 :
            cx = CENTER_X
            cy = CENTER_Y

        else :
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

        cv2.line(crop_image,(cx,0),(cx,720),(255,0,0),1)
        cv2.line(crop_image,(0,cy),(1280,cy),(255,0,0),1)
        cv2.drawContours(crop_image, contours, -1, (0,255,0), 1)

        if cx <= CENTER_X - 10:
            print "Turn Left!"

        elif cx < CENTER_X + 10 and cx > CENTER_X - 10 :
            print "On Track!"

        elif cx >= CENTER_X + 10:
            print "Turn Right"

    else:
        print "I don't see the line"
        cx = 0
        cy = 0
        print 'here'

    # Display the resulting frame
    #cv2.imshow('frame',crop_image)
    #cv2.imshow('mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q') :
        print "interrupt!"

    return cx, cy

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()

        
