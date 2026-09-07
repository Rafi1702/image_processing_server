from asyncio import coroutines
from data.datasource import image_data_source
from dataclasses import dataclass, field
import numpy as np
from abc import ABC, abstractmethod

directions = [[0, 1], [0, -1], [1, 0], [-1, 0]]

#Actually, Node index and list of nodes index is different due to adding source and sink node (Soon it will be change or deprecated)
@dataclass
class Node():
    index: int
    source_w: float
    sink_w: float
    edges: list[int] = field(default_factory=list[int]) 
    pixels: list[int] = field(default_factory=list[int]) 

class GraphBuilder(ABC):
    def __init__(self, image_width: int, image_height: int):
        self.image_width: int = image_width
        self.image_height: int = image_height

    @abstractmethod
    def build_graph(self):
        pass


class GraphBuilderOpenCv(GraphBuilder):
    def __init__(self, image_width: int, image_height: int, source:np.ndarray):
        super().__init__(image_width, image_height)
        self.nodes: list[Node] = []
        self._source = source
        self.build_graph()
        

    def __add_bidirectional_edge(self, edge_1, edge_2):
        self.nodes[edge_1].edges.append(edge_2)
        self.nodes[edge_2].edges.append(edge_1)

    @property
    def original_source(self) -> np.ndarray : 
        return self._source

    #Source and Sink Node is at index 0 and len(nodes)
    def build_graph(self):
        self.nodes.append(Node(-1, 0.0, 0.0, []))
        num_pixels = self.image_width * self.image_height
        num_channels = self._source.size // num_pixels if num_pixels > 0 else 4

        for row in range(self.image_height):
            for col in range(self.image_width):
                pixel_id = (row * self.image_width + col)
                source_color_idx = pixel_id * num_channels
                pixel_color = self._source[source_color_idx : source_color_idx + num_channels].tolist()
                self.nodes.append(Node(pixel_id, 0.0, 0.0, [], pixel_color))     

        self.nodes.append(Node(self.image_width * self.image_height, 0.0, 0.0, []))                               
                        
              
        ##To access node dont forget to add 1 (because -1 is sink node)  
        print("len nodes: ", len(self.nodes))    
        print("width * height: ", self.image_width * self.image_height)
        print("last nodes: ", self.nodes[0].pixels)    



class GraphBuilderFlatten(GraphBuilder):

    """ 
    Parameters:
    image_source (numpy array): the original image buffer
    pixel_format (int): the length representing 1 pixel, Ex. (RGB = 3) (RGBA = 4)
    """
    def __init__(self, image_width: int, image_height: int, image_source,  pixel_format:int = 4) :
        super().__init__(image_height=image_height, image_width=image_width)
        self.pixel_format = pixel_format
        self.image_source = image_source
        self.copy = self.build_graph()
    
    """ The method that create a graph 
    Parameters:
    additional_nodes (int) = the additional node, in this case the algorithm (max-flow min-cut) need 2 additional nodes (Source and Sink)
    """
    def build_graph(self, additional_nodes: int = 2,):
        total_nodes = self.pixel_format + (self.pixel_format + additional_nodes)
        n = self.image_width * self.image_height
        return [
                0 if x % total_nodes >= self.pixel_format  
                else self.image_source[(x // total_nodes) * self.pixel_format + (x % total_nodes)] 
                for x in range(2*total_nodes)]

    """The method to assign calculated weight
    Parameters:
    source_weight (float) = the weight from the source to the pixel
    """
    def assign_weight_value(self, source_weight: float = 0.0, sink_weight: float = 0.0, neigbor_weights: list[float] = [0.0,0.0,0.0,0.0]):
        something = None   
        raise NotImplementedError()
    
