from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import logging
from utils.utils import add_text_to_image


class Play(QThread):
    
    changePixmap = pyqtSignal(QImage)

    def __init__(self, camera):
        super(QThread, self).__init__()
        self.logger = logging.getLogger("Player")
        self.active = False
        self.camera = camera
        
    def run(self):
        self.logger.info("Thread was started")
        self.active = True
        self.camera.camera.start_video_capture()
        self.camera.capturing = True
        
        while self.active:
            self.camera.snapshot()
            frame2 = cv2.cvtColor(self.camera.frame, cv2.COLOR_BGR2RGB)
            frame2 = add_text_to_image(
                frame2,
                self.camera.img_description,
                top_left_xy=(0, 10),
                font_scale=.7,
                font_thickness=1,
                font_color_rgb=(0, 162, 232),
            )
            h, w, ch = frame2.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame2.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)

    def stop_video(self):
        self.logger.info("Thread was stopped")
        self.active = False
        self.camera.capturing = False
        self.quit()
        
    def running(self):
        self.logger.info(f"Thread running status: {self.isRunning()}")
