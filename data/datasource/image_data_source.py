
from abc import ABC, abstractmethod

class ImageDataSource(ABC):
    @abstractmethod
    def get_images(self, imagePath: str) -> list[str]:
        pass




        