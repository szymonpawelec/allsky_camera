from PyQt5.QtCore import QThread
import cv2
import logging
import time
from filepaths import paths
from utils.utils import makedir
from datetime import date
import numpy as np
import os


class Histogram(QThread):
    def __init__(self, camera):
        super(QThread, self).__init__()
        self.logger = logging.getLogger("Histogram")
        self.camera = camera
        self.active = False
        self.width = camera.width
        self.height = camera.height

    @makedir
    def run(self):
        if self.camera.capturing:
            self.logger.info("Thread was started")
            self.active = True
            filename = "histogram.jpg"

            while self.active and self.camera.capturing:
                self.path = paths["database"] + str(date.today()) + paths["histogram"]

                if os.path.exists(self.path + filename):
                    histogram = cv2.imread(self.path + filename)
                else:
                    histogram = self.camera.frame
                    histogram = histogram[479:480, :, :]
                    cv2.imwrite(self.path + filename, histogram)

                histogram_updated = np.concatenate(
                    (
                        histogram,
                        self.camera.frame[479:480, :, :]
                    ),
                    axis=0)

                cv2.imwrite(self.path + filename, histogram_updated)

                time.sleep(24*3600/960)

        else:
            self.logger.warning("Cannot start recording: camera is not collecting the data")

    def stop_recording(self):
        self.logger.info("Thread was stopped")
        self.active = False
        self.quit()

    def running(self):
        self.logger.info(f"Thread running status: {self.isRunning()}")
