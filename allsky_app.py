from PyQt5.QtWidgets import QApplication
from interface.main_window import MainWindow
from utils.utils import setup_logger
from device.camera import Camera
from device.config import config
from filepaths import paths

import sys
import logging

setup_logger(logging.DEBUG, paths["log"])
logger = logging.getLogger(__name__)

camera = Camera(default_settings=config)

app = QApplication(sys.argv)

# setup main window settings
win = MainWindow(camera)

win.show()
logger.info("Starting app")

sys.exit(app.exec_())
