from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import logging

class Play(QThread):
    
    changePixmap = pyqtSignal(QImage)
    
    def __init__(self,camera):
        super(QThread,self).__init__()
        self.logger = logging.getLogger(__name__)
        self.ThreadActive = False
        self.camera = camera
        
    def run(self):
        self.logger.info("Thread was started")
        self.ThreadActive = True
        self.camera.camera.start_video_capture()
        self.camera.capturing = True
        
        while self.ThreadActive:
            self.camera.snapshot()
            frame2 = cv2.cvtColor(self.camera.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame2.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(frame2.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            # p = convertToQtFormat
            self.changePixmap.emit(p)

    def stop_video(self):
        self.logger.info("Thread was stopped")
        self.ThreadActive = False
        self.camera.capturing = False
        self.quit()
        
    def running(self):
        self.logger.info(f"Thread running status: {self.isRunning()}")