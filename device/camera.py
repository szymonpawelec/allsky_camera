import logging
import os
import argparse
import zwoasi as asi    #https://zwoasi.readthedocs.io/en/latest/index.html
import sys
import cv2
import numpy as np
import time


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
        
        # get image from camera as a stream of bytes
        image = self.camera.get_video_data(2*exposure+1500, blank_image)
    
        # convert bytes to numpy array/vector
        jpg_as_np = np.frombuffer(image, dtype=np.uint8)
        
        # convert into 3 channel picture
        self.frame = jpg_as_np.reshape(self.height, self.width, 3)
    
    def __del__(self):
        self.camera.close()
        self.logger.info("Camera was closed")
    
    def set_gain(self, gain):
        self.gain = gain
        self.camera.set_control_value(asi.ASI_GAIN, gain)
        self.logger.info(f"Gain set to: {self.gain}")
        
    def set_exposure(self, exposure):  # in seconds
        self.exposure = exposure
        self.camera.set_control_value(asi.ASI_EXPOSURE, int(self.exposure*1e6))  # microseconds
        self.logger.info(f"Exposure set to: {self.exposure}")
        
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
        
    def auto_exp(self, auto):
        self.autoExposure = auto
        # possible_settings = ('Exposure', 'Gain','WB_R', 'WB_B')
        
        self.camera.set_control_value(
            self.controls['Exposure']['ControlType'],
            self.controls['Exposure']['DefaultValue'],
            True)
  
    def auto_gain(self, auto):
        self.autoGain = auto
        # possible_settings = ('Exposure', 'Gain','WB_R', 'WB_B')
        
        self.camera.set_control_value(
            self.controls['Gain']['ControlType'],
            self.controls['Gain']['DefaultValue'],
            self.autoGain)
