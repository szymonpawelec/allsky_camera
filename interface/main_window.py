from threads.play import Play
from threads.record import Record, Timelapse
from threads.ping import Ping
from threads.scheduler import Scheduler
from threads.camera_settings import CameraSettingsMonitor
from threads.server import Server
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
import logging


class MainWindow(QMainWindow):
    def __init__(self, camera):
        super(MainWindow, self).__init__()
        
        self.camera = camera
        self.logger = logging.getLogger(__name__)
                
        self.th_ping = Ping()
        self.th_ping.start()

        self.th_scheduler = Scheduler(self)
        self.th_scheduler.start()
        
        self.th_server = Server(self.camera)
        self.th_server.start()
        
        self.setGeometry(0, 0, 1000, 525)
        self.setWindowTitle("Allsky Camera")
        self.init_ui()

        self.logger.debug("Main window is set up")

    def closeEvent(self, event):
        # destruct camera object when window is closed
        self.camera.__del__()
        super(QMainWindow, self).closeEvent(event)
        
    def set_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def init_ui(self):
        # setup threads
        self.th_play = Play(self.camera)
        self.th_record = Record(self.camera)
        self.th_lapse = Timelapse(self.camera)
        
        # create a image label
        self.label = QtWidgets.QLabel(self)
        self.label.move(320, 0)
        self.label.resize(640, 480)
        self.th_play.changePixmap.connect(self.set_image)
        
        # setup PLAY video button
        self.but_play = QtWidgets.QPushButton(self)
        self.but_play.setText("Play Video")
        self.but_play.move(0, 0)
        self.but_play.clicked.connect(self.th_play.start)
        
        # setup STOP video button
        self.but_stop = QtWidgets.QPushButton(self)
        self.but_stop.setText("STOP Video")
        self.but_stop.move(100, 0)
        self.but_stop.clicked.connect(self.th_play.stop_video)      
        
        # setup RECORD video button
        self.but_rec = QtWidgets.QPushButton(self)
        self.but_rec.move(0, 30)
        self.but_rec.setText("Record Video")
        self.but_rec.clicked.connect(self.th_record.start)
        
        # setup STOP RECORD video button
        self.but_stoprec = QtWidgets.QPushButton(self)
        self.but_stoprec.move(100, 30)
        self.but_stoprec.setText("STOP recording")
        self.but_stoprec.clicked.connect(self.th_record.stop_recording)
        
        # setup TIMELAPSE video button
        self.but_lapse = QtWidgets.QPushButton(self)
        self.but_lapse.move(0, 60)
        self.but_lapse.setText("Record Timelapse")
        self.but_lapse.clicked.connect(self.th_lapse.start)
        
        # setup STOP TIMELAPSE video button
        self.but_stop_lapse = QtWidgets.QPushButton(self)
        self.but_stop_lapse.move(100, 60)
        self.but_stop_lapse.setText("STOP timelapse")
        self.but_stop_lapse.clicked.connect(self.th_lapse.stop_recording)

        # create a label for camera settings
        self.lab_cam_settings = QtWidgets.QLabel(self)
        self.lab_cam_settings.setGeometry(10, 475, 1000, 50)
        self.lab_cam_settings.setText("N/A")

        self.camera_settings = CameraSettingsMonitor(self.camera, self.lab_cam_settings)
        self.camera_settings.start()

        # auto exposure
        self.check_autoexp = QtWidgets.QCheckBox(self)
        self.check_autoexp.setText("Auto exposure")
        self.check_autoexp.move(0, 90)
        self.check_autoexp.setChecked(self.camera.auto_exposure)
        self.check_autoexp.stateChanged.connect(lambda: self.camera.set_auto_exp(self.check_autoexp.isChecked()))

        # auto gain
        self.check_autogain = QtWidgets.QCheckBox(self)
        self.check_autogain.setText("Auto gain")
        self.check_autogain.move(0, 120)
        self.check_autogain.setChecked(self.camera.auto_gain)
        self.check_autogain.stateChanged.connect(lambda: self.camera.set_auto_gain(self.check_autogain.isChecked()))

        # exposure slider
        self.slider_exposure = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider_exposure.setGeometry(100, 150, 200, 50)
        self.slider_exposure.setMaximum(600)
        self.slider_exposure.setMinimum(1)
        self.slider_exposure.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_exposure.setTickInterval(10)
        self.slider_exposure.setValue(int(self.camera.exposure))
        self.slider_exposure.valueChanged.connect(lambda: self.camera.set_exposure(self.slider_exposure.value()/10))
        self.slider_exposure.valueChanged.connect(lambda: self.camera.set_auto_exp(False))
        self.slider_exposure.valueChanged.connect(lambda: self.check_autoexp.setChecked(self.camera.auto_exposure))

        self.label_exposure=QtWidgets.QLabel(self)
        self.label_exposure.move(0, 150)
        self.label_exposure.setText('Exposure = ')

        # gain slider
        self.slider_gain = QtWidgets.QSlider(Qt.Horizontal, self)
        self.slider_gain.setGeometry(100, 200, 200, 50)
        self.slider_gain.setMaximum(100)
        self.slider_gain.setMinimum(1)
        self.slider_gain.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_gain.setTickInterval(1)
        self.slider_gain.setValue(int(self.camera.gain))
        self.slider_gain.valueChanged.connect(lambda: self.camera.set_gain(self.slider_gain.value()))
        self.slider_gain.valueChanged.connect(lambda: self.camera.set_auto_gain(False))
        self.slider_gain.valueChanged.connect(lambda: self.check_autogain.setChecked(self.camera.auto_gain))

        self.label_exposure=QtWidgets.QLabel(self)
        self.label_exposure.move(0, 200)
        self.label_exposure.setText('Gain = ')


        self.logger.debug("Interface was initialized")
