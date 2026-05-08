from dataclasses import dataclass
import numpy as np
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class Node():
    index: int
    weight: float
    nodes: list['Node']

class GraphBuilder(Generic[T],ABC):
    def __init__(self):
        self.nodes: list[Node] = []

    @abstractmethod
    def build_graph(self, source: T, image_width: int, image_height: int):
        pass


class GraphBuilderOpenCv(GraphBuilder[np.ndarray]):
    def __init__(self):
        super().__init__()
        

    def build_graph(self, source: np.ndarray, image_width: int, image_height: int):
        for row in range(image_height):
            for col in range(image_width):
                #TODO: get actual index from flatten rgba channel (r,g,b,a,r,g,b,a, ...)
                actual_index = (row * image_width + col) * 4

                node = Node(actual_index, 0.0, [])
                self.nodes.append(node)
            
        print("nodes: ", len(self.nodes))



# [[121,122,123],[121,122,123],[121,122,123]]