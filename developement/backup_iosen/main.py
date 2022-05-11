# ///////////////////////////////////////////////////////////////
#
# BY: EZOUAGH YOUNESS
# PROJECT MADE WITH: Qt Designer and PyQt5
# V: 1.0.1
#
# python3 -Xfaulthandler main.py
# @xset s off
# @xset -dpms
# ///////////////////////////////////////////////////////////////
# import faulthandler; faulthandler.enable()
import os.path
import sys
import platform
import json
# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
import time

from PyQt5 import QtCore, QtGui, QtWidgets
import requests
from tflite_runtime.interpreter import Interpreter
import numpy as np
from time import time, sleep
import cv2
from threading import Thread
import atexit
import RPi.GPIO as GPIO
from motor import motor
from datetime import datetime

from modules import *
from modules import Ui_MainWindow, Settings

# SET AS GLOBAL WIDGETS
# /////////////////////////////////////////////////////////////// pyside6-rcc resources.qrc -o resources_rc.py
widgets = None

# GLOBALS
# ///////////////////////////////////////////////////////////////

# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # GPIO.cleanup()
        # self.save_operation(0)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(14, GPIO.OUT)
        GPIO.setup(15, GPIO.OUT)
        self.pwm=GPIO.PWM(14, 50)
        self.pwm.start(0)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=self.set_photo_and_predict, bouncetime=20)
        GPIO.add_event_detect(24, GPIO.FALLING, callback=self.set_opened, bouncetime=20)
        self.result_count = [0, 0, 0, 0]
        self.app_path = "/home/pi/"#os.path.abspath(os.getcwd())
        self.userId = 1
        self.lights(0)
        self.t = time()
        self.isopen = False
        # SET AS GLOBAL WIDGETS
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        self.settings = None
        widgets = self.ui
        self.page = "home_page"
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        self.listenToTriggers()

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()
        self.showMaximized()
        widgets.rightButtons.hide()
        # Start intelligent agent
        # ///////////////////////////////////////////////////////////////iosen/
        print(self.app_path)
        self.interpreter = Interpreter(model_path=os.path.join(self.app_path, "iosen/model/my_modelv2b0.tflite"))
        self.interpreter.allocate_tensors()
        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()[0]['index']
        self.output_details = self.interpreter.get_output_details()[0]['index']
        _, self.height, self.width, channels = self.interpreter.get_input_details()[0]['shape']
        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home_page)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

    # ///////////////////////////////////////////////////////////////
    def listenToTriggers(self):
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_admin.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)
        # ///////////////////////////////////////////////////////////////

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        # SHOW HOME PAGE
        if btnName == "btn_home":
            self.showPage(btn, widgets.home_page)
        # SHOW camera PAGE
        elif btnName == "btn_admin":
            self.showPage(btn, widgets.admin_page)
        # ///////////////////////////////////////////////////////////////////////////////////
        # Exit App
        elif btnName == "btn_exit":
            self.exitApp()

    def exitApp(self):
        box = QMessageBox()
        box.setStyleSheet(Settings.BOX_THEME)
        box.setText("Do you want to exit the application?")
        box.setWindowTitle("Exiting the application!")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        choice = box.exec()
        if choice == QMessageBox.Yes:
            #self.M1.move_to(0)
            GPIO.cleanup()
            self.close()

    def save_img(self, img, user_class=""):
        x = Thread(target=self.save_image, args=(img,user_class))
        x.start()
        
    def save_image(self, img, user_class=""):
        class_name = "admin"+self.getClass(self.getClassfromRadioButton()) if self.page == "admin_page" else user_class
        image_save_path = os.path.join(self.app_path,"iosen", "dataset", "images", class_name)
        if not os.path.exists(image_save_path):
            os.mkdir(image_save_path)
        image_save_path = os.path.join(image_save_path,
                                       class_name + "_" + str(self.userId) + "_" + datetime.now().strftime(
                                           "%Y_%m_%d_%H%M%S") + ".jpg")
        cv2.imwrite(image_save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    def showClassOnRadioButton(self, class_id):
        widgets.radioButton_cam_glass1.setStyleSheet("")
        widgets.radioButton_cam_metal1.setStyleSheet("")
        widgets.radioButton_cam_plastic1.setStyleSheet("")
        widgets.radioButton_cam_other1.setStyleSheet("")
        if class_id == 1:
            widgets.radioButton_cam_glass1.setStyleSheet("QRadioButton::indicator {border:6px solid rgb(0, 255, 0);background: rgb(255, 0, 0);}")
        elif class_id == 0:
            widgets.radioButton_cam_metal1.setStyleSheet("QRadioButton::indicator {border:6px solid rgb(0, 255, 0);background: rgb(255, 0, 0);}")
        elif class_id == 3:
            widgets.radioButton_cam_plastic1.setStyleSheet("QRadioButton::indicator {border:6px solid rgb(0, 255, 0);background: rgb(255, 0, 0);}")
        else:
            widgets.radioButton_cam_other1.setStyleSheet("QRadioButton::indicator {border:6px solid rgb(0, 255, 0);background: rgb(255, 0, 0);}")

    def getClassfromRadioButton(self):
        if widgets.radioButton_cam_glass1.isChecked():
            return 1
        elif widgets.radioButton_cam_metal1.isChecked():
            return 0
        elif widgets.radioButton_cam_plastic1.isChecked():
            return 3
        elif widgets.radioButton_cam_other1.isChecked():
            return 2
        else:
            return -1
        
    def set_opened(self, ch):
        GPIO.remove_event_detect(24)
        if self.isopen == False:
            self.isopen = True
        
    def door(self):
        x = Thread(target=self.open_door, args=())
        x.start()
        
    def closed(self, chanel):
        GPIO.remove_event_detect(4)
        self.pwm.ChangeDutyCycle(0)
        
    def open_door(self):
        self.pwm.ChangeDutyCycle(10)
        sleep(7)
        self.pwm.ChangeDutyCycle(5) # left -90 deg position
        GPIO.add_event_detect(4, GPIO.FALLING, callback=self.closed, bouncetime=20)
        
    def lights(self, on):
        GPIO.output(15, on)
        # print("is open")
        
    def save_operation(self, cat=-1):
        x = Thread(target=self.postRequest, args=("http://sendacar.ddns.net:8321/iot/api/v1/operation",cat))
        x.start()
        
    def postRequest(self, url, data):
        r = requests.post(url,str(data)+",1")
        print(r.text)

    def set_photo_and_predict(self, ch):
        #GPIO.remove_event_detect(23)
        if (time() - self.t) >= 2 and self.isopen == True:
            # GPIO.remove_event_detect(24)
            self.isopen = False
            print("is closed")
            self.t = time()
            self.lights(1)
            self.update_status("Processing...")
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
            cap.set(cv2.CAP_PROP_FPS, 30)
            # sleep(0.2)
            ret, frame = cap.read()
            if not ret:
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2_im = frame.copy()
            self.lights(0)
            self.door()
            cv2_im = cv2.resize(cv2_im, (self.height, self.width))
            img_array = np.asarray(cv2_im * 1. / 255, dtype='float32')
            predictions = self.lite_model(img_array[None, ...])[0]
            y_lite = np.argmax(predictions)
            #self.save_operation(y_lite)
            # self.move_motor(y_lite)
            print("res = "+str(y_lite))
            cap.release()
            # self.play(y_lite)
            img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            class_name = self.getClass(y_lite)
            if self.page == "admin_page":
                widgets.label_camera_image1.setPixmap(QPixmap.fromImage(img))
                widgets.label_camera_result1.setText(class_name)
                self.showClassOnRadioButton(y_lite)
            else:
                widgets.label_camera_image2.setPixmap(QPixmap.fromImage(img))
                self.result_count[y_lite] += 1
                self.get_result_widget(y_lite).setText(" : " + str(self.result_count[y_lite]))
            self.save_img(frame, class_name)
            self.update_status("Waiting for an Object!...")            # print(time() - self.t)
            #self.isopen = False
            GPIO.add_event_detect(24, GPIO.FALLING, callback=self.set_opened, bouncetime=20)
            
    @staticmethod
    def getClass(index):
        return ["Metal", "Glass", "Other", "Plastic"][index]

    @staticmethod
    def get_result_widget(index):
        return [widgets.label_camera_result2_2, widgets.label_camera_result2_3, widgets.label_camera_result2_4,
                widgets.label_camera_result2_1][index]

    def update_status(self, msg):
        if self.page == "admin_page":
            widgets.label_camera_result1.setText(msg)
        else:
            widgets.label_camera_result2_5.setText(msg)

    def lite_model(self, image):
        self.interpreter.set_tensor(self.input_details, image)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details)

    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def showPage(self, btn, page):
        if self.page != page.objectName():
            self.page = page.objectName()
            widgets.stackedWidget.setCurrentWidget(page)  # SET PAGE
            UIFunctions.resetStyle(self, btn.objectName())  # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))  # SELECT MENU
            if self.page == "admin_page":
                widgets.rightButtons.show()
            else:
                widgets.rightButtons.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Yezvision40.png"))
    window = MainWindow()
    sys.exit(app.exec())
