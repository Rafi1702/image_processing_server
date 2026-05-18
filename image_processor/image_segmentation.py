
from dataclasses import dataclass
from image_processor.graph_util import GraphBuilder
from abc import ABC, abstractmethod

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

    def segmentation(self,fg_boundary_points: set[SegmentationBoundaryPoint], bg_boundary_points: set[SegmentationBoundaryPoint]):
        pass


class GraphCutImageSegmentation(GraphBasedImageSegmentation):
    def __init__(self, graph: GraphBuilder):
        super().__init__(graph) 
    
    def segmentation(self, bg_boundary_points: set[SegmentationBoundaryPoint], fg_boundary_points: set[SegmentationBoundaryPoint]):
        graph = self.graph.nodes

        for node_idx, node in enumerate(graph):
            if(node_idx == -1 or node_idx == len(graph) -1):
                continue

            node_y = node.index // self.graph.image_width
            node_x = node.index % self.graph.image_width
            
            if(SegmentationBoundaryPoint(node_x, node_y) in fg_boundary_points):
                node.sink_w = float('inf')
                node.source_w = 0.0
                print(f"Foreground point matched at node index {node.index} (x={node_x}, y={node_y})")
                print(f"Sink Weight: {node.sink_w}, Source Weight: {node.source_w}")
            elif(SegmentationBoundaryPoint(node_x, node_y) in bg_boundary_points):
                node.source_w = float('inf')
                node.sink_w = 0.0
                print(f"Background point matched at node index {node.index} (x={node_x}, y={node_y})")
                print(f"Sink Weight: {node.sink_w}, Source Weight: {node.source_w}")
            
        
        pass

class ThresholdingImageSegmentation(ImageSegmentation):
    def __init__(self):
        super().__init__()

    def segmentation(self):
        pass