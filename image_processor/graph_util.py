from asyncio import coroutines
from data.datasource import image_data_source
from dataclasses import dataclass, field
import numpy as np
from abc import ABC, abstractmethod

directions = [[0, 1], [0, -1], [1, 0], [-1, 0]]


def remove_duplicates(list):
    copy = []
    for e in list:
        if e not in copy:
            copy.append(e)    
    
    return copy

#Actually, Node index and list of nodes index is different due to adding source and sink node (Soon it will be change or deprecated)
@dataclass
class Node():
    index: int
    source_w: float
    sink_w: float
    edges: list[int] = field(default_factory=list[int]) 
    pixels: list[int] = field(default_factory=list[int]) 

class GraphBuilder[T](ABC):
    def __init__(self, image_width: int, image_height: int):
        self.nodes: list[Node] = []
        self.image_width: int = image_width
        self.image_height: int = image_height

    @abstractmethod
    def build_graph(self, source: T):
        pass


class GraphBuilderOpenCv(GraphBuilder[np.ndarray]):
    def __init__(self, image_width: int, image_height: int, source:np.ndarray):
        super().__init__(image_width, image_height)
        self._source = source
        #Source Node        
        self.nodes.append(Node(-1, 0.0, 0.0, []))
        
        num_pixels = self.image_width * self.image_height
        num_channels = source.size // num_pixels if num_pixels > 0 else 4

        for row in range(self.image_height):
            for col in range(self.image_width):
                pixel_id = (row * self.image_width + col)
                source_color_idx = pixel_id * num_channels
                pixel_color = source[source_color_idx : source_color_idx + num_channels].tolist()
                self.nodes.append(Node(pixel_id, 0.0, 0.0, [], pixel_color))

        ##todo add sink node
        self.nodes.append(Node(self.image_width * self.image_height, 0.0, 0.0, []))

    def __add_bidirectional_edge(self, edge_1, edge_2):
        self.nodes[edge_1].edges.append(edge_2)
        self.nodes[edge_2].edges.append(edge_1)

    @property
    def original_source(self) -> np.ndarray : 
        return self._source

    #Source and Sink Node is at index 0 and len(nodes)
    def build_graph(self):
        for row in range(self.image_height):
            for col in range(self.image_width):
                pixel_id = (row * self.image_width + col)
                node_index_in_list = pixel_id + 1 # Offset by 1 because Source Node is at index 0
                temporary_edges = []

                # Connect pixel to Source (-1) and Sink (W*H)
                temporary_edges.append(-1)
                temporary_edges.append(self.image_width * self.image_height)

                # Connect pixel to valid neighbors
                for direction in directions:
                    target_row = row + direction[0]
                    target_col = col + direction[1]
                    if target_row >= 0 and target_row < self.image_height and target_col >= 0 and target_col < self.image_width:
                        target_pixel_id = (target_row * self.image_width + target_col)
                        temporary_edges.append(target_pixel_id)
                    
                self.nodes[node_index_in_list].edges = temporary_edges

             

        ##Set source and sink edges using Node.index (0 to W*H-1)
        #source: index 0
        source_edges = list(range(self.image_width * self.image_height))
        self.nodes[0].edges = source_edges
        
        # sink: index len(nodes) - 1
        # Sink also connects to all pixels (0 to W*H-1)
        sink_edges = list(range(self.image_width * self.image_height))
        self.nodes[(self.image_width * self.image_height + 1)].edges = sink_edges                                      
                        
              
        ##To access node dont forget to add 1 (because -1 is sink node)  
        print("len nodes: ", len(self.nodes))    
        print("width * height: ", self.image_width * self.image_height)
        print("last nodes: ", self.nodes[0].pixels)    
