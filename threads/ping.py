from PyQt5.QtCore import QThread
import os
import time
import logging

class Ping(QThread):
    def __init__(self):
        super(QThread,self).__init__()
        self.logger = logging.getLogger("Ping")
        self.ThreadActive = False
        
    def run(self):
        self.ThreadActive = True
               
        self.logger.info("Ping thread is active")
        while self.ThreadActive:
            response = os.system("ping -n 1 www.google.com")
            self.logger.debug(f"Ping response : + {response}")
            time.sleep(360)
 
    def stop(self):
        self.logger.info("Thread was stopped")
        self.ThreadActive = False
        self.quit()
