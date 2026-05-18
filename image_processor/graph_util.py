from asyncio import coroutines
from data.datasource import image_data_source
from dataclasses import dataclass, field
import numpy as np
from abc import ABC, abstractmethod

directions = [[0, 1], [0, -1], [1, 0], [-1, 0]]

@dataclass
class Node():
    index: int
    source_w: float
    sink_w: float
    edges: list[int]
    pixels: list[int] = field(default_factory=list[int]) 

class GraphBuilder[T](ABC):
    def __init__(self):
        self.nodes: list[Node] = []
        self.image_width: int = 0
        self.image_height: int = 0

    @abstractmethod
    def build_graph(self, source: T, image_width: int, image_height: int):
        pass


class GraphBuilderOpenCv(GraphBuilder[np.ndarray]):
    def __init__(self):
        super().__init__()
        

    def build_graph(self, source: np.ndarray, image_width: int, image_height: int):
        self.image_width = image_width
        self.image_height = image_height
        #Sink Node        
        self.nodes.append(Node(-1, 0.0, 0.0, []))

        for row in range(image_height):
            for col in range(image_width):
                pixel_id = (row * image_width + col)
                source_color_idx = pixel_id * 4
                source_r = source[source_color_idx]
                source_g = source[source_color_idx + 1]
                source_b = source[source_color_idx + 2]
                self.nodes.append(Node(pixel_id, 0.0, 0.0, [],[source_r, source_g, source_b]))

        #Source Node
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
                        temporary_edges.append(target_pixel_id)
                    
                self.nodes[pixel_id + 1].edges = temporary_edges 
            
        source_edges = list(range(image_width * image_height))
        self.nodes[0].edges = source_edges

        sink_edges = list(range(image_width * image_height))
        self.nodes[(image_width * image_height)+1].edges = sink_edges                                      
                        
              
        ##To access node dont forget to add 1 (because -1 is sink node)  
        print("nodes: ", self.nodes[self.nodes[1].edges[0] + 1])    



