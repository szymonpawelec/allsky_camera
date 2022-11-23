import logging
import os
from filepaths import paths
from datetime import date
from logging.handlers import TimedRotatingFileHandler
from functools import wraps
import datetime as dt
from typing import Optional, Tuple
import cv2
import numpy as np


def is_day_hour(start, end):
    start_time_h = int(start[0:2])
    start_time_m = int(start[3:5])
    end_time_h = int(end[0:2])
    end_time_m = int(end[3:5])
    start_time = dt.time(start_time_h, start_time_m)
    end_time = dt.time(end_time_h, end_time_m)
    now_time = dt.datetime.now().time()
    if start_time < end_time:
        return now_time >= start_time and now_time <= end_time
    else:
        # Over midnight:
        return now_time >= start_time or now_time <= end_time


def makedir(func):
    # @wraps
    def wrapper(*args, **kwargs):
        os.makedirs(paths["database"] + str(date.today()) + paths["log"], exist_ok=True)
        os.makedirs(paths["database"] + str(date.today()) + paths["records"], exist_ok=True)
        os.makedirs(paths["database"] + str(date.today()) + paths["timelapse"], exist_ok=True)
        func(*args, **kwargs)
    return wrapper


class DirTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, **kwargs):
        TimedRotatingFileHandler.__init__(self, **kwargs)
    
    @makedir
    def emit(self, record):
        """
        Emit a record.

        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        filename = paths["database"] + str(date.today()) + paths["log"] + str(date.today()) + "_log.csv"
        self.baseFilename = os.path.abspath(filename)
        try:
            if self.shouldRollover(record):
                self.doRollover()
            logging.FileHandler.emit(self, record)
        except Exception:
            self.handleError(record)


def setup_logger(level, path):
    logger = logging.getLogger(__name__)
    
    logging.basicConfig(level = level)
    
    formatter = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s',
                                  "%Y-%m-%d %H:%M:%S")
    
    handler = DirTimedRotatingFileHandler(
        filename = paths["database"] + str(date.today()) + paths["log"] + str(date.today()) + "_log.csv",
        when='midnight',
        interval=0,
        backupCount=0,
        encoding=None,
        delay=True,
        utc=False,
        atTime=None)
    
    handler.suffix = "%Y-%m-%d_%H-%M-%S" + ".csv"
    handler.setFormatter(formatter)
    
    logging.getLogger('').addHandler(handler)
    
    logger.debug("Logger is set up.")


def add_text_to_image(
    image_rgb: np.ndarray,
    label: str,
    top_left_xy: Tuple = (0, 0),
    font_scale: float = 1,
    font_thickness: float = 1,
    font_face=cv2.FONT_HERSHEY_SIMPLEX,
    font_color_rgb: Tuple = (0, 0, 255),
    bg_color_rgb: Optional[Tuple] = None,
    outline_color_rgb: Optional[Tuple] = None,
    line_spacing: float = 1,
):
    """
    https://stackoverflow.com/questions/27647424/opencv-puttext-new-line-character
    Adds text (including multi line text) to images.
    You can also control background color, outline color, and line spacing.

    outline color and line spacing adopted from: https://gist.github.com/EricCousineau-TRI/596f04c83da9b82d0389d3ea1d782592
    """
    OUTLINE_FONT_THICKNESS = 3 * font_thickness

    im_h, im_w = image_rgb.shape[:2]

    for line in label.splitlines():
        x, y = top_left_xy

        # ====== get text size
        if outline_color_rgb is None:
            get_text_size_font_thickness = font_thickness
        else:
            get_text_size_font_thickness = OUTLINE_FONT_THICKNESS

        (line_width, line_height_no_baseline), baseline = cv2.getTextSize(
            line,
            font_face,
            font_scale,
            get_text_size_font_thickness,
        )
        line_height = line_height_no_baseline + baseline

        if bg_color_rgb is not None and line:
            # === get actual mask sizes with regard to image crop
            if im_h - (y + line_height) <= 0:
                sz_h = max(im_h - y, 0)
            else:
                sz_h = line_height

            if im_w - (x + line_width) <= 0:
                sz_w = max(im_w - x, 0)
            else:
                sz_w = line_width

            # ==== add mask to image
            if sz_h > 0 and sz_w > 0:
                bg_mask = np.zeros((sz_h, sz_w, 3), np.uint8)
                bg_mask[:, :] = np.array(bg_color_rgb)
                image_rgb[
                    y : y + sz_h,
                    x : x + sz_w,
                ] = bg_mask

        # === add outline text to image
        if outline_color_rgb is not None:
            image_rgb = cv2.putText(
                image_rgb,
                line,
                (x, y + line_height_no_baseline),  # putText start bottom-left
                font_face,
                font_scale,
                outline_color_rgb,
                OUTLINE_FONT_THICKNESS,
                cv2.LINE_AA,
            )
        # === add text to image
        image_rgb = cv2.putText(
            image_rgb,
            line,
            (x, y + line_height_no_baseline),  # putText start bottom-left
            font_face,
            font_scale,
            font_color_rgb,
            font_thickness,
            cv2.LINE_AA,
        )
        top_left_xy = (x, y + int(line_height * line_spacing))

    return image_rgb
