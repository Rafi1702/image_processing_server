from ..image_data_source import ImageDataSource
import cv2 as cv
import numpy as np

from dataclasses import dataclass


@dataclass
class ImageData:
    image: np.ndarray
    width: int
    height: int

class ImageDataSourceOpenCvImpl(ImageDataSource[ImageData]):
    def get_images(self, imagePath: str) -> ImageData:        
        img = cv.imread(imagePath, cv.IMREAD_UNCHANGED)
        if img is None: 
            raise Exception("Image not found")
        # print("image: ", img)
        # print("shape: ", img.shape)

        ##assume the image is already bgra
        #TODO: Create a check to check the image is bgra

        img_rgba = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)

        return ImageData(img_rgba.flatten(), img.shape[1], img.shape[0])





        
        

