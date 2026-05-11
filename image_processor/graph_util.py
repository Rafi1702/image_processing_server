from data.datasource import image_data_source
from dataclasses import dataclass
import numpy as np
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

directions = [[0, 1], [0, -1], [1, 0], [-1, 0]]
@dataclass
class Edge():
    target_index: int
    weight: float

@dataclass
class Node():
    index: int
    source_w: float
    sink_w: float
    edges: list[Edge]

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
        
        self.nodes.append(Node(-1, 0.0, 0.0, []))

        for row in range(image_height):
            for col in range(image_width):
                pixel_id = (row * image_width + col)
                self.nodes.append(Node(pixel_id, 0.0, 0.0, []))

        
# Node Sink
        self.nodes.append(Node((image_width * image_height)+1, 0.0, 0.0, []))

        for row in range(image_height):
            for col in range(image_width):
                pixel_id = (row * image_width + col)
                temporary_edges = []
                for direction in directions:
                    target_row = row + direction[0]
                    target_col = col + direction[1]
                    
                  
                    if target_row >= 0 and target_row < image_height and target_col >= 0 and target_col < image_width:
                        target_pixel_id = (target_row * image_width + target_col)
                        target_color_idx = target_pixel_id * 4
                        target_r = source[target_color_idx]
                        target_g = source[target_color_idx + 1]
                        target_b = source[target_color_idx + 2]
                        
                        edge = Edge(target_pixel_id, 0.0)
                        temporary_edges.append(edge)
                    
                self.nodes[pixel_id].edges = temporary_edges 
            
        source_edges = []
        for i in range((image_width * image_height)):
            source_edges.append(Edge(i, 0.0))

        self.nodes[0].edges = source_edges

        sink_edges = []
        for i in range((image_width * image_height)):
            sink_edges.append(Edge(i, 0.0))
        
        self.nodes[(image_width * image_height)+1].edges = sink_edges                                      
                        
              

        print("nodes: ", self.nodes[0].index)    



