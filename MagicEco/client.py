#!usr/bin/env python
# -*- coding: utf-8 -*-



import sys, os
import sys,time,http.client
from urllib.request import urlopen
import requests
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QDesktopServices



# default setting
HOST = '192.168.137.86'
PORT = '8000'
BASE_URL = "http://"+HOST +':' + PORT + '/'
action = 'run/?action='
key = 0
Running_screen = "Running.ui"
Login_screen = "login.ui"
Ui_Running_screen, QtBaseClass   = uic.loadUiType(Running_screen)
Ui_Login_screen, QtBaseClass   = uic.loadUiType(Login_screen)


def __reflash_url__():
    global BASE_URL, HOST, PORT
    BASE_URL = "http://"+HOST +':' + PORT + '/'

def __read_auto_inf__():
    try:
        fp = open("auto_ip.inf", 'r')
        lines = fp.readlines()
        for line in lines:
            if "ip" in line:
                ip = line.replace(' ', '').replace('\n','').split(':')[1]

            elif "port" in line:
                port = line.replace(' ', '').replace('\n','').split(':')[1]

            elif "remember_status" in line:
                remember_status = line.replace(' ', '').replace('\n','').split(':')[1]
        fp.close()
        return ip, port, int(remember_status)
    except IOError:
        return -1

def __write_auto_inf__(ip=None, port=None, rem_status=None):
    fp = open("auto_ip.inf", 'w')
    string = "ip: %s \nport: %s\nremember_status: %s\n" %(ip, port, rem_status)
    fp.write(string)
    fp.close()


class login_screen(QtWidgets.QDialog,Ui_Login_screen):
    """login screen
    """
    def __init__(self):
        
        global autologin
        global HOST,PORT
        #self.app = QtWidgets.QApplication(sys.argv)
        info = __read_auto_inf__()
        if info == -1:
            HOST = ''
            PORT = ''
            autologin = -1
        else:
            HOST = info[0]
            PORT = info[1]
            autologin = info[2]

        QtWidgets.QDialog.__init__(self)	
        Ui_Login_screen.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Login Screen")
        if autologin == 1:
            self.HostEdit.setText(HOST)
            self.PortEdit.setText(PORT)
            self.checkBox.setChecked(True)

        else:
            self.HostEdit.setText("")
            self.PortEdit.setText("")
            self.checkBox.setChecked(False)

    def on_LoginButton_pressed(self):
        
        global HOST,PORT,autologin
        HOST = self.HostEdit.text()
        PORT = self.PortEdit.text()
        __reflash_url__()
        if connection_ok() == True:
            print("connection complete")
            if autologin == 1:
                HOST = self.HostEdit.text()
                PORT = self.PortEdit.text()
            else:
                HOST=""
                PORT=""

            __write_auto_inf__(HOST,PORT,autologin)
            HOST = self.HostEdit.text()
            PORT = self.PortEdit.text()
            self.close()
            start.startstream()
            start.show()

            return True
        else:
            QMessageBox.about(self,"LOGIN FAILED","Check your HOST and PORT again.")
            print("connection failed")
            return False
    def on_checkBox_pressed(self):

        global autologin
        autologin = -autologin
        print('autolongin = %s'%autologin) 
        print ("on_checkBox_clicked", HOST,autologin)


class run(QtWidgets.QDialog,Ui_Running_screen):
    """running screen
    """

    def __init__(self):
        #self.app = QtWidgets.QApplication(sys.argv)
        #global HOST,PORT
        #url = "http://" + HOST + ":8080/?action=stream"
        QtWidgets.QDialog.__init__(self)
        Ui_Running_screen.__init__(self)
        self.setupUi(self)
        #self.RunningScreen.load(QtCore.QUrl(url))

    def startstream(self):
        global HOST, PORT
        url = "http://" + HOST + ":8080/?action=stream"
        self.RunningScreen.load(QtCore.QUrl(url))

    #key press event
    def keyPressEvent(self,event):
        key_press = event.key()

        if not event.isAutoRepeat():
            if key_press == Qt.Key_Up:
                run_action('camup')
            if key_press == Qt.Key_Right:
                run_action('camright')
            if key_press == Qt.Key_Down:
                run_action('camdown')
            if key_press == Qt.Key_Left:
                run_action('camleft')
            if key_press == Qt.Key_W:
                run_action('forward')
            if key_press == Qt.Key_A:
                run_action('fwleft')
            if key_press == Qt.Key_S:
                run_action('backward')
            if key_press == Qt.Key_D:
                run_action('fwright')
    #key release event
    def keyReleaseEvent(self,event):
        key_release = event.key()
        if not event.isAutoRepeat():
            if key_release == Qt.Key_Up:
                run_action('camready')
            if key_release == Qt.Key_Right:
                run_action('camready')
            if key_release == Qt.Key_Down:
                run_action('camready')
            if key_release == Qt.Key_Left:
                run_action('camready')
            if key_release == Qt.Key_W:
                run_action('stop')
            if key_release == Qt.Key_A:
                run_action('fwstraight')
            if key_release == Qt.Key_S:
                run_action('stop')
            if key_release == Qt.Key_D:
                run_action('fwstraight')
    def on_VoiceButton_pressed(self):
        url = QtCore.QUrl('C:/xampp/htdocs/magiceco/efuture.html')
        QDesktopServices.openUrl(url)
    def on_level1_clicked(self):
        run_speed("1")
    def on_level2_clicked(self):
        run_speed("10")
    def on_level3_clicked(self):
        run_speed("50")
    def on_level4_clicked(self):
        run_speed("100")
    def on_level5_clicked(self):
        run_speed("99")

    def on_LineTracker_clicked(self):
        global BASE_URL
        url=BASE_URL+"run/?linetrack"
        r=requests.get(url)
        if r.text=='End':
            pass
        #exec (open("line_tracker_finish.py").read())
    #def on_BallTracker_clicked(self):
    def on_ParkingButton_pressed(self):
        global BASE_URL
        url=BASE_URL+"run/?parking"
        r=requests.get(url)
        if r.text=='Alert':
            QMessageBox.about(self,"Alert","Your car is under attack!!!!!!!")

    def on_DetectButton_pressed(self):
        global BASE_URL
        url=BASE_URL+"run/?detect"
        r=requests.get(url)
        if int(r.text) <= 30 :
            str="Something is "+r.text+"cm behind. Be careful!"
            QMessageBox.about(self,"Alert",str)
        elif int(r.text) > 30 and int(r.text) < 200 :
            str = "Something is " + r.text + "cm in front of your way. Don't worry"
            QMessageBox.about(self,"Alert",str)
        else :
            str = "I cannot detect anything"
            QMessageBox.about(self, "Alert", str)




#request to server
def __request__(url,times = 10):
    for x in range(times):
        try:
            requests.get(url)
            print('received url : %s'%url)
            return 0
        except:
            print("connection error!")
        print("abort!")

#set speed
def run_speed(speed):
    global BASE_URL
    url = BASE_URL + "run/?speed=" + speed
    __request__(url)

#draw command from keypress and send to __request__
def run_action(cmd):
    global BASE_URL
    action = 'run/?action='
    url = BASE_URL + action + cmd
    __request__(url)

def connection_ok(): 
    global BASE_URL
    cmd = 'connection_test'
    url = BASE_URL  + cmd
    print('url: %s'% url)
    # if server find there is 'connection_test' in request url, server will response 'Ok'

    try:
        r=requests.get(url)
        if r.text == 'OK':
            return True
    except :
        return False


def main():
    app = QtWidgets.QApplication(sys.argv)
   
    login = login_screen()
    start = run()
    login.show()
    #start.show()
    print("client2 ended")
    sys.exit(app.exec_())

#start first
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
   
    login = login_screen()
    start = run()
    login.show()
    #start.show()
    print("client2 ended")
    sys.exit(app.exec_())
    



    
