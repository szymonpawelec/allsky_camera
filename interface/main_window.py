from threads.play import Play
from threads.record import Record, Timelapse
from threads.ping import Ping
from threads.server import Server
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
import logging


class MainWindow(QMainWindow):
    def __init__(self,camera):
        super(MainWindow, self).__init__()
        
        self.camera = camera
        self.logger = logging.getLogger(__name__)
                
        self.ping = Ping()
        self.ping.start()
        
        self.server = Server(self.camera)
        self.server.start()
        
        self.setGeometry(0,0,1000,600)
        self.setWindowTitle("All Sky Project")
        self.initUI()
        self.logger.debug("Main window is set up")    

        
        
    def closeEvent(self, event):
        # destruct camera object when window is closed
        self.camera.__del__()
        super(QMainWindow, self).closeEvent(event)
        
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
        
    def initUI(self):
        
        # setup threads
        self.th_play = Play(self.camera)
        self.th_record = Record(self.camera)
        self.th_lapse = Timelapse(self.camera)
        
        # create a image label
        self.label = QtWidgets.QLabel(self)
        self.label.move(320, 0)
        self.label.resize(640, 480)
        self.th_play.changePixmap.connect(self.setImage)
        
        #setup PLAY video button
        self.but_play = QtWidgets.QPushButton(self)
        self.but_play.setText("Play Video")
        self.but_play.move(0,0)
        self.but_play.clicked.connect(self.th_play.start)
        
        #setup STOP video button
        self.but_stop = QtWidgets.QPushButton(self)
        self.but_stop.setText("STOP Video")
        self.but_stop.move(100,0)
        self.but_stop.clicked.connect(self.th_play.stop_video)      
        
        #setup RECORD video button
        self.but_rec = QtWidgets.QPushButton(self)
        self.but_rec.move(0,30)
        self.but_rec.setText("Record Video")
        self.but_rec.clicked.connect(self.th_record.start)
        
        #setup STOP RECORD video button
        self.but_stoprec = QtWidgets.QPushButton(self)
        self.but_stoprec.move(100,30)
        self.but_stoprec.setText("STOP recording")
        self.but_stoprec.clicked.connect(self.th_record.stop_recording)
        
        #setup TIMELAPSE video button
        self.but_lapse = QtWidgets.QPushButton(self)
        self.but_lapse.move(0,60)
        self.but_lapse.setText("Record Timelapse")
        self.but_lapse.clicked.connect(self.th_lapse.start)
        
        #setup STOP TIMELAPSE video button
        self.but_stop_lapse = QtWidgets.QPushButton(self)
        self.but_stop_lapse.move(100,60)
        self.but_stop_lapse.setText("STOP timelapse")
        self.but_stop_lapse.clicked.connect(self.th_lapse.stop_recording)
        
        #setup TEMPORARY button
        self.but_temp = QtWidgets.QPushButton(self)
        self.but_temp.setText("temporary")
        self.but_temp.move(200,30)
        self.but_temp.clicked.connect(self.th_record.set_resolution)
        

        self.logger.debug("Interface was initialized")