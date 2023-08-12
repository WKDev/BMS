#-*- coding: utf-8 -*-

from tools.flir_with_cv import FlirCV
from tools.flir_common import Flir
from tools.temperature import TempSensor
from tools.pt100 import PT100
from tools.blink_detector_dlib import BlinkDetectorDlib
from tools.db import db, Table
from tools.dust_sensor import PMS7003
from flask import Flask, render_template, Response, request, redirect, url_for
import RPi.GPIO as GPIO

import os
from datetime import time

GPIO.setmode(GPIO.BCM)
## gpio for relay
GPIO.setup(25, GPIO.OUT)


"""
    <Camera Metadata>
    169.254.202.73
    subnet 255.255.0.0
    gateway 0.0.0.0
"""
CAMERA_IP = "169.254.202.73"
OVERLAY = "on"
ENCODING = "mjpg"

app = Flask(__name__, static_folder='static')
flirImg = FlirCV(camera_ip=CAMERA_IP,
                encoding=ENCODING,
                overlay=OVERLAY)
flirData = Flir(baseURL= "http://" + CAMERA_IP+"/")

TARGET_TEMP = 28
temp_sensor1 =TempSensor(sensor_name = "28-0000000364a0") # atmosphere
temp_sensor2 =TempSensor(sensor_name = "28-00000003e755") # water tank
temp_sensor3 =PT100() # output temp

# DUST SENSOR
dust = PMS7003()

# DB
basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'db.sqlite')

# Initial Heating Mode
heat_mode = "off"  # 0 : AUTO , 1 : MANUAL
heater = "OFF"
temperature = None


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'jqiowejrojzxcovnklqnweiorjqwoijroi'

MAINTAIN_ROWS = 10

db.init_app(app)
db.app = app

with app.app_context():
    db.create_all()

blinkImg = BlinkDetectorDlib(db= db, app=app)

## chson comment : 얼굴이 찾아지면 강제로 확대
blinkImg.dynamic_zoom(True)

@app.before_first_request
def before_first_request():
    # cam_mode initial state
    global cam_mode
    cam_mode = "FLIR"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        mode = request.form.get("mode")
        if mode == "auto":
            # auto mode work conduction
            print("auto mode 입니다.")
            pass
        elif mode == "manual":
            slider_value = request.form['slider_value']
            print("manual mode 입니다.")
            # auto mode work conduction
            pass

    if Table.query.count() > MAINTAIN_ROWS:
        oldest = Table.query.order_by(Table.id).first()
        db.session.delete(oldest)
        db.session.commit()
        print("[index] leaving 10 things")
    tables = Table.query.all()

    return render_template('index.html', tables=tables)

@app.route('/camera')
def camera_stream():
    global cam_mode
    # cam_mode = request.form.get("cam_mode")
    if cam_mode == "FLIR" :
        return Response(flirImg.getFramesForFlask(), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cam_mode == "IR" :
        return Response(blinkImg.getFramesForFlask(), mimetype='multipart/x-mixed-replace; boundary=frame')

#TODO make mode change functions, MSX, IR, VISUAL -> OK
@app.route('/change_cam_mode', methods=["POST"])
def change_cam_mode():
    mode = request.form.get("mode")
    global cam_mode
    cam_mode = request.form.get("cam_mode")
    if mode == "VIS" : flirData.setVisualMode()
    elif mode == "MSX" : flirData.setMSXMode()
    elif mode == "IR" : flirData.setIRMode()
    return "OK"

@app.route('/update')
def update():
    return {
        'temperature1': temp_sensor1.read_temp(),
        'temperature2': temp_sensor2.read_temp()
    }

@app.route('/update_heater', methods=["POST", "GET"])
def update_heater():
    global heat_mode, heater, temperature
    # post 수동
    # get on off 상태만 가져와
    # get
    if request.method == 'POST':
        data = request.get_json()
        print(data)
        heat_mode = data.get("mode")
        temperature = data.get("temperature")
        print("포스트")
        return {
            'heater' : heater
        }
    elif request.method == "GET":
        # 자동 모드일 때 처리하는 코드
        if heat_mode == "on":
            print("수동")
            # 수동 모드일 때 처리하는 코드
            if temperature is not None:
                # 온도 값이 전송된 경우, 해당 온도 값으로 히터를 제어할 수 있습니다.
                if float(temp_sensor1.read_temp()) < TARGET_TEMP or float(temp_sensor2.read_temp())< TARGET_TEMP:
                    print("1켜짐")
                    heater = "ON"
                    GPIO.output(25, GPIO.LOW)

                else:
                    heater = "OFF"
                    GPIO.output(25, GPIO.HIGH)

                    print("1꺼짐")
            else:
                print("2꺼짐")
                # 온도 값이 전송되지 않은 경우, 기본 온도 값을 사용합니다.
                heater = "OFF"
                GPIO.output(25, GPIO.HIGH)

            return {
            'heater': heater
        }
        else:
            # 자동 모드일 때 처리하는 코드
            print("자동")
            if float(temp_sensor1.read_temp()) < TARGET_TEMP or float(temp_sensor2.read_temp())< TARGET_TEMP:
                print("3켜짐")
                heater = "ON"
                GPIO.output(25, GPIO.LOW)

            else:
                print("3꺼짐")
                heater = "OFF"
                GPIO.output(25, GPIO.HIGH)

            return {
                'heater': heater
            }

@app.route('/update_pt')
def update_pt():
    return {
        'temperature3': temp_sensor3.read_temp()
    }
@app.route('/update_dust')
def update_dust():
    return dust.read_dust()

@app.route('/update_baby_temp')
def update_baby_temp():
    return {"baby_temperature" : flirData.getMaxTemp()}

@app.route('/process_slider', methods=['POST'])
def process_slider():
    value = request.form['value']
    print("!!!value")
    return 'Success'

#TODO Underdeveloped
# @app.route('/temp_control_mode')
# def temp_control_mode():
#     target_temp = 24
#     current_temp = None
#     Heater = None
#     if current_temp > target_temp:
#         Heater = True
#     else:
#         Heater = False

@app.route('/temp_control_auto',methods=['POST'])
def temp_control_auto():
    print("자동 모드입니다.")
    return "AUTO MODE"

@app.route('/temp_control_manual',methods=['POST'])
def temp_control_manual():
    slider_value = request.form.get('slider_value')
    print("수동 모드입니다.slider_value: ", slider_value)
    return "MANUAL MODE"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    GPIO.cleanup()
