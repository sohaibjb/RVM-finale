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
import qrcode
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
from PIL import Image
from datetime import datetime
import base64
from phpserialize import dumps  # pip install phpserialize
from Crypto.Cipher import AES  # pip install pycrypto
import hmac
import hashlib
from modules import *
from modules import Ui_MainWindow, Settings
from modules.messagebox import Ui_messagebox

# GPIO.setwarnings(False)
# SET AS GLOBAL WIDGETS
# /////////////////////////////////////////////////////////////// pyside6-rcc resources.qrc -o resources_rc.py
widgets = None
options_widgets = None


# GLOBALS
# ///////////////////////////////////////////////////////////////

# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(14, GPIO.OUT)
        GPIO.setup(15, GPIO.OUT)
        self.pwm = GPIO.PWM(14, 50)
        self.pwm.start(0)
        GPIO.add_event_detect(23, GPIO.FALLING, callback=self.set_photo_and_predict, bouncetime=20)
        GPIO.add_event_detect(24, GPIO.FALLING, callback=self.set_opened, bouncetime=20)
        self.result_count = [0, 0, 0, 0]
        self.app_path = "/home/pi/"  # os.path.abspath(os.getcwd())
        self.lights(0)
        self.t = time()
        self.isopen = False
        # /////////////  logo inside generated Qr code /////////////
        self.logo = Image.open('images/images/logo.png')
        # taking base width
        basewidth = 100
        # adjust image size
        hsize = int((float(self.logo.size[1]) * float((basewidth / float(self.logo.size[0])))))
        self.logo = self.logo.resize((basewidth, hsize), Image.ANTIALIAS)  # Image.ANTIALIAS
        self.QRcode = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            border=1
        )
        self.bin_id = "72f8a748e12daa6b9816ac9cae5ab52"
        self.key = base64.b64decode("fmDdWI3mPwzB/g5SrKmZileMX6dUarf7t5wx+MKb8Fk=")
        self.token = "12"  # None
        self.finish_counter = 60
        # SET AS GLOBAL WIDGETS
        global widgets
        global options_widgets

        # ///////////////////////////////////////////////////////////////
        widgets = Ui_MainWindow()
        options_widgets = Ui_messagebox()

        widgets.setupUi(self)
        self.options_window = QtWidgets.QMainWindow()
        options_widgets.setupUi(self.options_window)
        self.settings = None

        # self.page = "home_page"
        widgets.stackedWidget.setCurrentWidget(widgets.page)
        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)
        UIFunctions.uiDefinitions(self.options_window)
        UIFunctions.center(self.options_window)
        self.listenToTriggers()
        self.timer = QTimer()
        self.timer.timeout.connect(self.clock)
        self.clock()
        self.timer.start(1000)

        self.finish_timer = QTimer()
        self.finish_timer.timeout.connect(self.finish_timer_fct)
        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # Start intelligent agent
        # ///////////////////////////////////////////////////////////////iosen/
        self.interpreter = Interpreter(model_path=os.path.join(self.app_path, "iosen/model/my_modelv2b0.tflite"))
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()[0]['index']
        self.output_details = self.interpreter.get_output_details()[0]['index']
        _, self.height, self.width, channels = self.interpreter.get_input_details()[0]['shape']

    # ///////////////////////////////////////////////////////////////

    def listenToTriggers(self):
        # triggers for finish and help buttons
        widgets.butt_help.clicked.connect(self.exitApp)  # btn_help rename
        widgets.btn_help_1.clicked.connect(self.exitApp)
        widgets.btn_help_3.clicked.connect(self.exitApp)

        widgets.btn_echanger.clicked.connect(self.echanger)
        widgets.btn_finish.clicked.connect(self.finish)
        widgets.btn_restart.clicked.connect(self.recommencer)
        widgets.btn_start.clicked.connect(self.recommencer)
        widgets.btn_refresh.clicked.connect(self.reset_finish_timer)

        options_widgets.btn_scanqr.clicked.connect(self.scanqrbtn)
        options_widgets.btn_printer.clicked.connect(self.printerbtn)
        options_widgets.btn_donate.clicked.connect(self.donatebtn)

    def echanger(self):
        if sum(self.result_count) > 0:
            self.options_window.show()
        else:
            widgets.stackedWidget.setCurrentWidget(widgets.page)
        # self.options_window.show()

    def recommencer(self):
        self.token = None
        self.finish_timer.stop()
        if self.open_session():
            widgets.stackedWidget.setCurrentWidget(widgets.countingPage)
        else:
            widgets.stackedWidget.setCurrentWidget(widgets.page)

    def aesEncrypterCBC(self, value, iv):
        crypter = AES.new(key=self.key, mode=AES.MODE_CBC, IV=iv)
        return crypter.encrypt(value)

    def encrypt(self, data):
        iv = os.urandom(16)
        data = dumps(data)
        padding = 16 - len(data) % 16
        data += bytes(chr(padding) * padding, 'utf-8')
        value = base64.b64encode(self.aesEncrypterCBC(data, iv))
        iv = base64.b64encode(iv)
        mac = hmac.new(self.key, iv + value, hashlib.sha256).hexdigest()
        dic = {'iv': iv.decode(), 'value': value.decode(), 'mac': mac}
        return base64.b64encode(bytes(json.dumps(dic), 'utf-8')).decode()

    def scanqrbtn(self):
        # //////////////// Generate Qr code/////////////////////////////////////////////////////
        if self.token is not None:
            c = time()
            self.options_window.close()
            data = '{"1":"' + self.token + '"}'
            encrypted = self.encrypt(data)
            self.QRcode.add_data(encrypted)
            self.QRcode.make(fit=True)
            QRimg = self.QRcode.make_image(fill_color='black', back_color="white").convert('RGB')
            # set size of QR code
            pos = ((QRimg.size[0] - self.logo.size[0]) // 2, (QRimg.size[1] - self.logo.size[1]) // 2)
            QRimg.paste(self.logo, pos)
            frame = cv2.cvtColor(np.array(QRimg.convert('RGB'))[:, :, ::-1].copy(), cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (300, 300))
            img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            widgets.qr_image.setPixmap(QPixmap.fromImage(img))
            widgets.stackedWidget.setCurrentWidget(widgets.main_page)
            print(time() - c)
            # Start the counter with 60 seconds for the scan / restart procedure
            self.finish_counter = 60
            self.finish_timer.start(1000)
        else:
            self.finish()

    def printerbtn(self):
        pass

    def donatebtn(self):
        pass

    def help(self):
        # Help message box for contacting the support
        helpdial = QMessageBox()
        helpdial.setText("Here you can find our info to contact us ")
        helpdial.setStyleSheet("QLabel {min-width: 200px; min-height: 100px; }")
        helpdial.setInformativeText("phone number : +212600000000\n email : help@gmail.com")
        helpdial.setIcon(QMessageBox.Question)
        helpdial.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        helpdial.exec_()

    def clock(self):
        # Clock display for date and current time
        t = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')
        widgets.time_1.setText(t)  # time label on the start page
        widgets.time_2.setText(t)  # time label on the counting page
        widgets.time_3.setText(t)  # time label on the end page
        # widgets.level_p.setValue(20)

    def finish_timer_fct(self):
        # Finish counter that start from finish_counter = 60 down to 0 and display it on the button
        self.finish_counter += -1
        widgets.btn_finish.setText("Terminer (" + str(self.finish_counter) + ")")
        if self.finish_counter < 0:
            self.finish()

    def finish(self):
        self.finish_timer.stop()
        self.token = None
        widgets.stackedWidget.setCurrentWidget(widgets.page)

    def reset_finish_timer(self):
        # Reset the timer
        self.finish_counter = 60

    def exitApp(self):
        box = QMessageBox()
        box.setStyleSheet(Settings.BOX_THEME)
        box.setText("Do you want to exit the application?")
        box.setWindowTitle("Exiting the application!")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        choice = box.exec()
        if choice == QMessageBox.Yes:
            # self.M1.move_to(0)
            GPIO.cleanup()
            self.close()

    def save_img(self, img, user_class=""):
        x = Thread(target=self.save_image, args=(img, user_class))
        x.start()

    def save_image(self, img, class_name=""):
        image_save_path = os.path.join(self.app_path, "iosen", "dataset", "images", class_name)
        if not os.path.exists(image_save_path):
            os.mkdir(image_save_path)
        image_save_path = os.path.join(image_save_path,
                                       class_name + "_" + str(self.token) + "_" + datetime.now().strftime(
                                           "%Y_%m_%d_%H%M%S") + ".jpg")
        cv2.imwrite(image_save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

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
        self.pwm.ChangeDutyCycle(5)  # left -90 deg position
        GPIO.add_event_detect(4, GPIO.FALLING, callback=self.closed, bouncetime=20)

    def lights(self, on):
        GPIO.output(15, on)
        # print("is open")

    def save_operation(self, cat=-1):
        x = Thread(target=self.save_operation_thread,
                   args=("http://backup.sendatrack.com/iosen/api/session/operation/" + str(cat)))
        x.start()

    def save_operation_thread(self, url):
        is_ok = False
        attempts = 0
        while attempts < 2 and is_ok is False:
            attempts += 1
            t = round(time())
            secret = '{"' + str(t) + '":"' + str(self.token) + '"}'
            encrypted = self.encrypt(secret)
            is_ok = self.postRequest(url, encrypted)
            return is_ok is not False and is_ok.status_code == 201
        return False

    def open_session(self):
        is_ok = False
        attempts = 0
        while attempts < 2 and is_ok is False:
            attempts += 1
            t = round(time())
            secret = '{"' + str(t) + '":"' + str(self.bin_id) + '"}'
            encrypted = self.encrypt(secret)
            is_ok = self.postRequest("http://backup.sendatrack.com/iosen/api/session/open", encrypted)
            if is_ok is not False and is_ok.status_code == 201:
                self.token = r.text
                return True
        return False

    def postRequest(self, url, data):
        r = requests.post(url, data={"data": data}, headers={"Accept": "application/json"})
        # print(r.text)
        if r.status_code == 490:
            self.key = base64.b64encode(r.text)
            return False
        return r

        # pass

    def set_photo_and_predict(self, ch):
        if (time() - self.t) >= 2 and self.isopen is True and self.token is not None:
            self.isopen = False
            print("is closed")
            self.t = time()
            self.lights(1)
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
            cap.set(cv2.CAP_PROP_FPS, 30)
            ret, frame = cap.read()
            if not ret:
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2_im = frame.copy()
            self.lights(0)
            # self.door()
            cv2_im = cv2.resize(cv2_im, (self.height, self.width))
            img_array = np.asarray(cv2_im * 1. / 255, dtype='float32')
            predictions = self.lite_model(img_array[None, ...])[0]
            y_lite = np.argmax(predictions)
            self.save_operation(y_lite)
            print("res = " + str(y_lite))
            cap.release()
            class_name = self.getClass(y_lite)
            self.result_count[y_lite] += 1
            if class_name == "Metal":
                widgets.number_c.setText(str(self.result_count[y_lite]))
            elif class_name == "Plastic":
                widgets.number_p.setText(str(self.result_count[y_lite]))
            else:
                widgets.number_un.setText(str(sum(self.result_count[0:3:2])))
            widgets.total_number.setText(str(sum(self.result_count)))
            self.save_img(frame, class_name)
            GPIO.add_event_detect(24, GPIO.FALLING, callback=self.set_opened, bouncetime=20)

    @staticmethod
    def getClass(index):
        return ["Glass", "Metal", "Other", "Plastic"][index]

    def lite_model(self, image):
        self.interpreter.set_tensor(self.input_details, image)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Yezvision40.png"))
    window = MainWindow()
    sys.exit(app.exec())
