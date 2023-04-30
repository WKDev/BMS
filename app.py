from tools.flir_with_cv import FlirCV
from tools.flir_common import Flir
from tools.temperature import TempSensor
from tools.blink_detector_dlib import BlinkDetectorDlib
from tools.db import db, Table
from flask import Flask, render_template, Response, request, redirect, url_for

import os
from datetime import time
"""
    <Camera Metadata>
    169.254.202.73
    subnet 255.255.0.0
    gateway 0.0.0.0
"""
CAMERA_IP = "169.254.202.73"
OVERLAY = "on"
ENCODING = "mjpg"

app = Flask(__name__)
flirImg = FlirCV(camera_ip=CAMERA_IP,
                encoding=ENCODING,
                overlay=OVERLAY)
flirData = Flir(baseURL= "http://" + CAMERA_IP+"/")

temp_sensor1 =TempSensor(sensor_name = "28-0000000364a0")
temp_sensor2 =TempSensor(sensor_name = "28-00000003e755")

basdir = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(basdir, 'db.sqlite')

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
blinkImg.dynamic_zoom(True)

@app.before_first_request
def before_first_request():
    # cam_mode initial state
    global cam_mode
    cam_mode = "FLIR"

@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
    #     _sleeptime = request.form['sleeptime']
    #     new_table = Table(sleeptime=time(hour=4,minute=30,second=6))
    #     db.session.add(new_table)
    #     db.session.commit()
    #     print("[index] add row")

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

if __name__ == '__main__':
    app.run(host='192.168.0.190', port=5000)