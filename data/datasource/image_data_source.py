
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class ImageDataSource(Generic[T],ABC):
    @abstractmethod
    def get_images(self, image_path: str) -> T:
        pass




        