from PyQt5.QtCore import QThread
import logging
from utils.utils import is_day_hour
import time


class Scheduler(QThread):
    def __init__(self, interface):
        super(QThread, self).__init__()
        self.logger = logging.getLogger("Scheduler")
        self.ThreadActive = False
        self.interface = interface
        
    def run(self):
        self.ThreadActive = True
               
        self.logger.info("Thread is active")
        time.sleep(10)
        self.interface.th_play.start()

        while self.ThreadActive:
            # start timelapse thread
            if not is_day_hour('23:34', '23:35'):
                self.interface.th_lapse.start()
            elif self.interface.th_lapse.isRunning():
                self.interface.th_lapse.stop_recording()
                self.logger.info("Timelapse thread stopped")
                # restart server thread
                self.interface.th_server.stop()
                self.logger.info("Server thread stopped")
                time.sleep(1)
                self.interface.th_server.start()
                time.sleep(5)



            # time.sleep(60)

    def stop(self):
        self.logger.info("Thread was stopped")
        self.ThreadActive = False
        self.quit()
