from PyQt5.QtCore import QThread
import cv2
import logging
import time
from filepaths import paths
from utils.utils import makedir
from datetime import date, datetime
from utils.utils import add_text_to_image


class Record(QThread):
    def __init__(self, camera):
        super(QThread, self).__init__()
        self.logger = logging.getLogger("Record")
        self.camera = camera
        self.active = False
        self.rec_fps = 25
        self.width = camera.width
        self.height = camera.height

    @makedir
    def run(self):
        if self.camera.capturing:
            self.logger.info("Thread was started")
            self.active = True
            self.path = paths["database"] + str(date.today()) + paths["records"]
            filename = str(datetime.now().strftime('%Y-%m-%d_%H.%M.%S')) + ".mp4"

            print(self.path + filename)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(self.path + filename, fourcc, self.rec_fps, (self.width, self.height))

            while self.active and self.camera.capturing:
                if (self.camera.width != self.width) or (self.camera.height != self.height):
                    frame = cv2.resize(self.camera.frame, (self.width, self.height),
                                       fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                    frame = add_text_to_image(
                        frame,
                        self.camera.img_description,
                        top_left_xy=(0, 10),
                        font_scale=.7,
                        font_thickness=1,
                        font_color_rgb=(232, 162, 0),
                    )
                    out.write(frame)
                else:
                    frame = add_text_to_image(
                        self.camera.frame,
                        self.camera.img_description,
                        top_left_xy=(0, 10),
                        font_scale=.7,
                        font_thickness=1,
                        font_color_rgb=(232, 162, 0),
                    )
                    out.write(frame)

                time.sleep(1 / self.rec_fps)

            out.release()
        else:
            self.logger.warning("Cannot start recording: camera is not collecting the data")

    def stop_recording(self):
        self.logger.info("Thread was stopped")
        self.active = False
        self.quit()

    def running(self):
        self.logger.info(f"Thread running status: {self.isRunning()}")

    def set_resolution(self, par, res):
        if self.active:
            self.logger.warning("Cannot set resolution: camera is already recording")
        else:
            self.width = res[0]
            self.height = res[1]
            self.logger.info(f"Image resolution was set to: {self.width}x{self.height}")


class Timelapse(QThread):
    def __init__(self, camera):
        super(QThread, self).__init__()
        self.logger = logging.getLogger('Timelapse')
        self.camera = camera
        self.active = False
        self.rec_fps = 25
        self.timelapse = 5
        self.width = camera.width
        self.height = camera.height
        
    @makedir    
    def run(self):
        if self.camera.capturing:
            self.logger.info("Thread was started")
            self.active = True
            self.path = paths["database"] + str(date.today()) + paths["timelapse"]
            filename = str(datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))+".mp4"
            
            print(self.path + filename)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(self.path + filename, fourcc, self.rec_fps, (self.width,  self.height))
                    
            while self.active and self.camera.capturing:
                if (self.camera.width != self.width) or (self.camera.height != self.height):
                    frame = cv2.resize(self.camera.frame,(self.width,self.height),
                        fx=0, fy=0, interpolation = cv2.INTER_CUBIC)
                    frame = add_text_to_image(
                        frame,
                        self.camera.img_description,
                        top_left_xy=(0, 10),
                        font_scale=.7,
                        font_thickness=1,
                        font_color_rgb=(232, 162, 0),
                    )
                    out.write(frame)
                else:
                    frame = add_text_to_image(
                        self.camera.frame,
                        self.camera.img_description,
                        top_left_xy=(0, 10),
                        font_scale=.7,
                        font_thickness=1,
                        font_color_rgb=(232, 162, 0),
                    )
                    out.write(frame)
                
                time.sleep(self.timelapse)
                
            out.release()
        else:
            self.logger.warning("Cannot start timelapse: camera is not collecting the data")

    def stop_recording(self):
        self.logger.info("Thread was stopped")
        self.active = False
        self.quit()
        
    def running(self):
        self.logger.info(f"Thread running status: {self.isRunning()}")
    
    def set_resolution(self, par, res):
        if self.active:
            self.logger.warning("Cannot set resolution: camera is already recording")
        else:
            self.width = res[0]
            self.height = res[1]
            self.logger.info(f"Image resolution was set to: {self.width}x{self.height}")


class Snapshot(QThread):
    def __init__(self, camera):
        super(QThread, self).__init__()
        self.logger = logging.getLogger('Snapshot')
        self.camera = camera
        self.active = False
        self.width = camera.width
        self.height = camera.height

    @makedir
    def run(self):
        if self.camera.capturing:
            self.logger.info("Thread was started")
            self.active = True

            while self.active and self.camera.capturing:
                self.path = paths["database"] + str(date.today()) + paths["snapshot"]
                filename = str(datetime.now().strftime('%Y-%m-%d_%H.%M.%S')) + ".png"

                if (self.camera.width != self.width) or (self.camera.height != self.height):
                    frame = cv2.resize(self.camera.frame, (self.width, self.height),
                                       fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                    frame = add_text_to_image(
                        frame,
                        self.camera.img_description,
                        top_left_xy=(0, 10),
                        font_scale=.7,
                        font_thickness=1,
                        font_color_rgb=(232, 162, 0),
                    )
                    cv2.imwrite(self.path + filename, frame)
                    self.logger.info(f"Snapshot recorded:  {self.path + filename}")
                else:
                    frame = add_text_to_image(
                        self.camera.frame,
                        self.camera.img_description,
                        top_left_xy=(0, 10),
                        font_scale=.7,
                        font_thickness=1,
                        font_color_rgb=(232, 162, 0),
                    )
                    cv2.imwrite(self.path + filename, frame)
                    self.logger.info(f"Snapshot recorded:  {self.path + filename}")

                time.sleep(3600)

        else:
            self.logger.warning("Cannot start snapshot: camera is not collecting the data")

    def stop_recording(self):
        self.logger.info("Thread was stopped")
        self.active = False
        self.quit()

    def running(self):
        self.logger.info(f"Thread running status: {self.isRunning()}")

    def set_resolution(self, par, res):
        if self.active:
            self.logger.warning("Cannot set resolution: camera is already recording")
        else:
            self.width = res[0]
            self.height = res[1]
            self.logger.info(f"Image resolution was set to: {self.width}x{self.height}")