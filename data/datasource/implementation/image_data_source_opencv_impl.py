from ..image_data_source import ImageDataSource
import cv2 as cv
import numpy as np
import os

from dataclasses import dataclass
from PIL import Image

@dataclass
class ImageData:
    image: np.ndarray
    width: int
    height: int

class ImageDataSourceOpenCvImpl(ImageDataSource[ImageData]):
    def get_images(self, image_path: str) -> ImageData:       
        img = cv.imread(imagePath, cv.IMREAD_UNCHANGED)
        if img is None: 
            raise Exception("Image not found")

        img_rgba = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)

        return ImageData(img_rgba.flatten(), img.shape[1], img.shape[0])


class ImageDataSourcePilImpl(ImageDataSource[ImageData]):
    def get_images(self, image_path: str) -> ImageData:       
        with Image.open(image_path) as img:
            img_rgba = np.asarray(img.convert("RGBA"))
            return ImageData(img_rgba.flatten(), img_rgba.shape[1], img_rgba.shape[0])




    




        
        

