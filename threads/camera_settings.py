from PyQt5.QtCore import QThread
import os
import time
import logging


class CameraSettingsMonitor(QThread):
    def __init__(self, camera, label):
        super(QThread, self).__init__()
        self.camera = camera
        self.label = label
        self.logger=logging.getLogger("Camera settings")
        self.ThreadActive = False

    def run(self):
        self.ThreadActive = True

        self.logger.info("Camera settings thread is active")
        while self.ThreadActive:
            label_txt = 'Camera controls:'

            # get exposure time:
            self.camera.exposure = self.camera.camera.get_control_value(1)[0]/1e6
            label_txt += f"Exposure: {self.camera.exposure}"
            # get max auto exposure time:
            max_auto_exp = self.camera.camera.get_control_value(11)[0]/1e3
            label_txt += f"/{max_auto_exp}, "

            # get gain:
            self.camera.gain = self.camera.camera.get_control_value(0)[0]
            label_txt += f"Gain: {self.camera.gain}"
            # get max auto gain:
            max_auto_gain = self.camera.camera.get_control_value(10)[0]
            label_txt += f"/{max_auto_gain}, "

            # get Red/Blue:
            red = self.camera.camera.get_control_value(3)[0]
            blue = self.camera.camera.get_control_value(4)[0]
            label_txt += f"R: {red}, B: {blue} "

            self.label.setText(label_txt)

            time.sleep(1)

    def stop(self):
        self.logger.info("Thread was stopped")
        self.ThreadActive=False
        self.quit()
