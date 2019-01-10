import cv2
import numpy as np
from utils.app_utils import *

class VideoCamera(object):
    def __init__(self,file_path):
        self.M = None
        self.width = 400 # Set Phone width and height here
        self.height = 400
        self.image = None
        self.file_path = file_path
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        self.video = cv2.VideoCapture(file_path)
    
    def __del__(self):
       self.video.release()

    def set_rect(self, pts):
        pts1 = np.float32(pts)
        pts2 = np.float32([[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])
        self.M = cv2.getPerspectiveTransform(pts1, pts2)
    
    def get_frame(self):
        success, image = self.video.read()
        if success:
            self.image = image
            if self.M is not None:
                image = cv2.warpPerspective(image, self.M, (self.width, self.height))
            # We are using Motion JPEG, but OpenCV defaults to capture raw images,
            # so we must encode it into JPEG in order to correctly display the
            # video stream.
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tostring()
        else:
            self.video = cv2.VideoCapture(self.file_path)
            return open('outputs/temp.jpg', 'rb').read()


if __name__ == '__main__':
    vc = VideoCamera()
    vc.get_frame()
