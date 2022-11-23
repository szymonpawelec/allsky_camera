import logging
import os
import argparse
import zwoasi as asi    #https://zwoasi.readthedocs.io/en/latest/index.html
import sys
import cv2
import numpy as np
from datetime import datetime


class Camera:
    def __init__(self, default_settings):
        self.logger = logging.getLogger("Camera")
        
        env_filename = os.getenv('ZWO_ASI_LIB')
        
        parser = argparse.ArgumentParser(description='Process and save images from a camera')
        parser.add_argument('filename',
                            nargs='?',
                            help='SDK library filename')
        args = parser.parse_args()
        
        # Initialize zwoasi with the name of the SDK library
        if args.filename:
            asi.init(args.filename)
        elif env_filename:
            asi.init(env_filename)
        else:
            self.logger.error('The filename of the SDK library is required \
                              (or set ZWO_ASI_LIB environment variable with the filename)')
            sys.exit(1)
            
        self.num_cameras = asi.get_num_cameras()
        if self.num_cameras == 0:
            self.logger.error('No cameras found')
            sys.exit(0)
        
        self.cameras_found = asi.list_cameras()  # Models names of the connected cameras
               
        if self.num_cameras == 1:
            camera_id = 0
            self.logger.debug('Found one camera: %s' % self.cameras_found[0])
        else:
            self.logger.info('Found %d cameras' % self.num_cameras)
            for n in range(self.num_cameras):
                self.logger.info('    %d: %s' % (n, self.cameras_found[n]))
            # TO DO: allow user to select a camera
            camera_id = 0
            print('Using #%d: %s' % (camera_id, self.cameras_found[camera_id]))
            
        num_cameras = asi.get_num_cameras()
        if num_cameras == 0:
            self.logger.error("No cameras found")
            raise ValueError('No cameras found')
            
        self.camera_id = 0  # use first camera from list
        self.cameras_found = asi.list_cameras()
        self.logger.info(f"Cameras found: {self.cameras_found}")
        
        self.camera = asi.Camera(self.camera_id)
        self.controls = self.camera.get_controls()
        self.camera_info = self.camera.get_camera_property()
                        
        # Use 3x8-bit RGB mode:
        self.camera.set_image_type(asi.ASI_IMG_RGB24)
        
        # Use minimum USB bandwidth permitted
        self.camera.set_control_value(
            asi.ASI_BANDWIDTHOVERLOAD,
            self.camera.get_controls()['BandWidth']['MinValue'],
            auto=True)
        
        self.width = default_settings["width"]
        self.height = default_settings["height"]
        self.capturing = False
        self.img_description = None
        self.count = 1
        
        self.camera.disable_dark_subtract()
        self.set_gain(default_settings["gain"])
        self.set_exposure(default_settings["exposure"])
        self.set_gamma(default_settings["gamma"])
        self.set_brightness(default_settings["brightness"])
        self.set_flip(default_settings["flip"])
        self.set_color_balance(
            default_settings["whiteBalanceB"],
            default_settings["whiteBalanceR"],
            default_settings["whiteBalance"]
            )

        self.set_auto_exp(default_settings["autoExposure"])
        self.set_max_auto_exp(default_settings["max_auto_exp"])
        self.set_auto_gain(default_settings["autoGain"])
        self.set_max_auto_gain(default_settings["max_auto_gain"])

        self.logger.info("Camera was initialized successfully")

    def print_camera_controls(self):
        # Get camera controls
        print('')
        print('Camera controls:')
        for cn in sorted(self.controls.keys()):
            print('    %s:' % cn)
            for k in sorted(self.controls[cn].keys()):
                print('        %s: %s' % (k, repr(self.controls[cn][k])))            
                
    def snapshot(self):
        blank_image = bytearray(self.height*self.width*3)
        
        # get exposure time:
        exposure = self.camera.get_control_value(1)[0]

        self.set_img_description()
        # get image from camera as a stream of bytes
        try:
            image = self.camera.get_video_data(2*exposure+5000, blank_image)
        except Exception as e:
            print(e)
    
        # convert bytes to numpy array/vector
        jpg_as_np = np.frombuffer(image, dtype=np.uint8)
        
        # convert into 3 channel picture
        self.frame = jpg_as_np.reshape(self.height, self.width, 3)
        self.count += 1
    
    def __del__(self):
        self.camera.close()
        self.logger.info("Camera was closed")

    def set_img_description(self):
        label_txt = f"Time: {str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))}\n"
        label_txt += f"Frame number: {self.count}\n"
        # get exposure time:
        self.exposure = self.camera.get_control_value(1)[0] / 1e6
        label_txt += f"Exposure: {self.exposure}"
        # get max auto exposure time:
        max_auto_exp = self.camera.get_control_value(11)[0] / 1e3
        label_txt += f"/{max_auto_exp}\n"

        # get gain:
        self.gain = self.camera.get_control_value(0)[0]
        label_txt += f"Gain: {self.gain}"
        # get max auto gain:
        max_auto_gain = self.camera.get_control_value(10)[0]
        label_txt += f"/{max_auto_gain}\n"

        # get Red/Blue:
        red = self.camera.get_control_value(3)[0]
        blue = self.camera.get_control_value(4)[0]
        label_txt += f"R: {red}, B: {blue}\n"

        self.img_description = label_txt
    
    def set_gain(self, gain):
        self.gain = gain
        self.camera.set_control_value(asi.ASI_GAIN, gain)
        self.logger.info(f"Gain set to: {self.gain}")

    def set_max_auto_gain(self, max_gain):
        self.max_gain = max_gain
        self.camera.set_control_value(asi.ASI_AUTO_MAX_GAIN, max_gain)
        self.logger.info(f"Max auto gain set to: {self.max_gain}")

    def set_exposure(self, exposure):  # in seconds
        self.exposure = exposure
        self.camera.set_control_value(asi.ASI_EXPOSURE, int(self.exposure*1e6))  # microseconds
        self.logger.info(f"Exposure set to: {self.exposure}")

    def set_max_auto_exp(self, max_exp):
        self.max_exp = max_exp
        self.camera.set_control_value(asi.ASI_AUTO_MAX_EXP, max_exp * 1000)
        self.logger.info(f"Max auto exposure set to: {self.max_exp}")

    def set_gamma(self, gamma):
        self.gamma = gamma
        self.camera.set_control_value(asi.ASI_GAMMA, self.gamma)
        self.logger.info(f"Gamma set to: {self.gamma}")

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.camera.set_control_value(asi.ASI_GAMMA, self.gamma)
        self.logger.info(f"Brightness set to: {self.brightness}")
    
    def set_color_balance(self, white_balance_b, white_balance_r, white_balance):
        self.white_balance_b = white_balance_b
        self.white_balance_r = white_balance_r
        self.white_balance = white_balance
        self.camera.set_control_value(asi.ASI_WB_B, white_balance_b, white_balance)
        self.camera.set_control_value(asi.ASI_WB_R, white_balance_r, white_balance)
        self.logger.info(f"Blue channel balance set to: {self.white_balance_b}")
        self.logger.info(f"Red channel balance set to: {self.white_balance_r}")
        self.logger.info(f"Auto color balance is: {self.white_balance}")
    
    def set_flip(self, flip):
        self.flip = flip
        self.camera.set_control_value(asi.ASI_FLIP, flip)
        self.logger.info(f"Camera image flip: {self.flip}")
        
    def set_auto_exp(self, auto):
        # possible_settings = ('Exposure', 'Gain','WB_R', 'WB_B')
        self.auto_exposure = auto
        self.camera.set_control_value(
            self.controls['Exposure']['ControlType'],
            self.camera.get_control_value(1)[0],
            auto)
        self.logger.info(f"Auto exposure set to: {self.auto_exposure}")
  
    def set_auto_gain(self, auto):
        # possible_settings = ('Exposure', 'Gain','WB_R', 'WB_B')
        self.auto_gain = auto
        self.camera.set_control_value(
            self.controls['Gain']['ControlType'],
            self.gain,
            auto)
        self.logger.info(f"Auto gain set to: {self.auto_gain}")
