from ..image_data_source import ImageDataSource
import cv2 as cv

class ImageDataSourceOpenCvImpl(ImageDataSource):
    def get_images(self, imagePath: str) -> list[str]:        
        img = cv.imread(imagePath, cv.IMREAD_UNCHANGED)
        if img is None:
            raise Exception("Image not found")
        print("image: ", img)
        print("shape: ", img.shape)
        return []





        
        

