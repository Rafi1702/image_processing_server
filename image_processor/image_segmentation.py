
from dataclasses import dataclass
from image_processor.graph_util import GraphBuilder
from abc import ABC, abstractmethod
from image_processor.distribution_model import GaussianModel
import numpy as np

@dataclass(frozen=True)
class SegmentationBoundaryPoint:
    x: int
    y: int
    
class ImageSegmentation:
    def __init__(self, ):
        pass
    
    @abstractmethod
    def segmentation(self):
        pass


class GraphBasedImageSegmentation(ImageSegmentation):
    def __init__(self, graph: GraphBuilder):
        super().__init__() 
        self.graph = graph 

    def segmentation(self):
        pass


class GraphCutImageSegmentation(GraphBasedImageSegmentation):
    def __init__(self, graph: GraphBuilder, fg_boundary_points: set[SegmentationBoundaryPoint], bg_boundary_points: set[SegmentationBoundaryPoint]):
        super().__init__(graph) 
        self.fg_boundary_points = fg_boundary_points
        self.bg_boundary_points = bg_boundary_points
    
    def segmentation(self):
        graph = self.graph.nodes
        fg_pixels = []
        bg_pixels = []

        for boundary_point in self.fg_boundary_points:
            pixel_index = boundary_point.y * self.graph.image_width + boundary_point.x
            fg_pixels.append(self.graph.nodes[pixel_index + 1].pixels)
        for boundary_point in self.bg_boundary_points:
            pixel_index = boundary_point.y * self.graph.image_width + boundary_point.x
            bg_pixels.append(self.graph.nodes[pixel_index + 1].pixels)

    
        fg_distribution = GaussianModel(source=np.array(fg_pixels, dtype=np.float64), n_components=2)
        bg_distribution = GaussianModel(source=np.array(bg_pixels, dtype=np.float64), n_components=2)
        
        print("len fg_distribution", fg_distribution.model.means_)
        print("len bg_distribution", bg_distribution.model.means_)
        # for node_idx, node in enumerate(graph):
        #     if(node.index == -1 or node.index == len(graph)):
        #         continue

        #     node_y = node.index // self.graph.image_width
        #     node_x = node.index % self.graph.image_width
            
        #     if(SegmentationBoundaryPoint(node_x, node_y) in self.fg_boundary_points):
        #         node.sink_w = float('inf')
        #         node.source_w = 0.0
        #         print(f"Foreground point matched at node index {node.index} (x={node_x}, y={node_y})")
        #         print(f"Sink Weight: {node.sink_w}, Source Weight: {node.source_w}")
        #     elif(SegmentationBoundaryPoint(node_x, node_y) in self.bg_boundary_points):
        #         node.source_w = float('inf')
        #         node.sink_w = 0.0
        #         print(f"Background point matched at node index {node.index} (x={node_x}, y={node_y})")
        #         print(f"Sink Weight: {node.sink_w}, Source Weight: {node.source_w}")
        #     else:
        #         #TODO: CALCULATE WEIGHT USING DISTRIBUTION PROBABILITY P(fg|I) , P(bg|I)

        #         pass
            
        
        pass

class ThresholdingImageSegmentation(ImageSegmentation):
    def __init__(self):
        super().__init__()

    def segmentation(self):
        pass