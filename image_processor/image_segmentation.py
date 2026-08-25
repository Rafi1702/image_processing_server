
from dataclasses import dataclass
from image_processor.graph_util import GraphBuilder
from abc import ABC, abstractmethod
from image_processor.distribution_model import GaussianModel
import numpy as np
import cv2 as cv
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow, breadth_first_order

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

        if len(fg_pixels) == 0 or len(bg_pixels) == 0:
            print("[Segmentation Error] Both foreground and background scribbles are required.")
            return

        fg_distribution = GaussianModel(source=np.array(fg_pixels, dtype=np.float64), n_components=2)
        bg_distribution = GaussianModel(source=np.array(bg_pixels, dtype=np.float64), n_components=2)

        H, W = self.graph.image_height, self.graph.image_width
        N = H * W
        V = N + 2

        # 1. Gather all pixel colors
        all_colors = np.array([node.pixels for node in self.graph.nodes[1:-1]], dtype=np.float64)

        print("all_colors shape: ", all_colors.shape)
        # 2. Compute GMM log likelihoods (scores)
        # score_samples returns log-likelihood. Negative log-likelihood is our cost.
        fg_scores = -fg_distribution.model.score_samples(all_colors)
        bg_scores = -bg_distribution.model.score_samples(all_colors)
        
        print("fg_scores: ", fg_scores)
        print("bg_scores: ", bg_scores)
   
        # 3. Setup Source (S=0) and Sink (T=V-1) t-link capacities
        source_w = bg_scores.copy()
        sink_w = fg_scores.copy()

        # Override for seed pixels
        large_val = 1e9
        fg_seed_indices = [pt.y * W + pt.x for pt in self.fg_boundary_points]
        bg_seed_indices = [pt.y * W + pt.x for pt in self.bg_boundary_points]

        source_w[fg_seed_indices] = large_val
        sink_w[fg_seed_indices] = 0

        source_w[bg_seed_indices] = 0
        sink_w[bg_seed_indices] = large_val

        # 4. Construct n-link capacities between adjacent pixels
        # Reshape to compute spatial differences
        img_rgb = all_colors.reshape((H, W, 3))
        
        # Horizontal differences: (H, W-1, 3)
        diff_h = img_rgb[:, :-1, :] - img_rgb[:, 1:, :]
        sq_diff_h = np.sum(diff_h ** 2, axis=2)

        # Vertical differences: (H-1, W, 3)
        diff_v = img_rgb[:-1, :, :] - img_rgb[1:, :, :]
        sq_diff_v = np.sum(diff_v ** 2, axis=2)

        # Compute beta = 1 / (2 * mean(sq_diff))
        mean_sq_diff = (np.sum(sq_diff_h) + np.sum(sq_diff_v)) / (sq_diff_h.size + sq_diff_v.size)
        if mean_sq_diff == 0:
            mean_sq_diff = 1e-5
        beta = 1.0 / (2.0 * mean_sq_diff)

        # Compute capacities w = gamma * exp(-beta * sq_diff)
        gamma = 50.0
        w_h = gamma * np.exp(-beta * sq_diff_h)
        w_v = gamma * np.exp(-beta * sq_diff_v)

        # Vectorized assembly of horizontal neighbors
        y_indices_h, x_indices_h = np.ogrid[:H, :W-1]
        p1_h = y_indices_h * W + x_indices_h
        p2_h = p1_h + 1
        u_h = p1_h.flatten() + 1
        v_h = p2_h.flatten() + 1
        weight_h = w_h.flatten()

        # Vectorized assembly of vertical neighbors
        y_indices_v, x_indices_v = np.ogrid[:H-1, :W]
        p1_v = y_indices_v * W + x_indices_v
        p2_v = p1_v + W
        u_v = p1_v.flatten() + 1
        v_v = p2_v.flatten() + 1
        weight_v = w_v.flatten()

        # Symmetrical n-links
        u_neighbors = np.concatenate([u_h, v_h, u_v, v_v])
        v_neighbors = np.concatenate([v_h, u_h, v_v, u_v])
        weight_neighbors = np.concatenate([weight_h, weight_h, weight_v, weight_v])

        # S-link: 0 -> pixel (node index: pixel_id + 1)
        u_source = np.zeros(N, dtype=np.int32)
        v_source = np.arange(1, N + 1, dtype=np.int32)
        weight_source = source_w

        # T-link: pixel -> V-1
        u_sink = np.arange(1, N + 1, dtype=np.int32)
        v_sink = np.ones(N, dtype=np.int32) * (V - 1)
        weight_sink = sink_w

        # Combine all edges into coordinate lists
        rows = np.concatenate([u_neighbors, u_source, u_sink])
        cols = np.concatenate([v_neighbors, v_source, v_sink])
        data = np.concatenate([weight_neighbors, weight_source, weight_sink])

        # 5. Build capacity CSR matrix 
        # SciPy's maximum_flow requires integer capacities.
        # We scale float weights by 1000 to preserve precision.
        scale_factor = 1000.0
        data_int = (data * scale_factor).astype(np.int64)
        capacity_matrix = csr_matrix((data_int, (rows, cols)), shape=(V, V), dtype=np.int64)

        # 6. Execute Min-Cut Max-Flow
        print(f"[Segmentation] Executing max-flow on graph with {V} nodes...")
        result = maximum_flow(capacity_matrix, 0, V - 1)
        print(f"[Segmentation] Max flow: {result.flow_value / scale_factor:.2f}")

        # Compute residual graph
        residual = capacity_matrix - result.flow
        
        # Filter negative or zero capacity edges
        residual.data[residual.data <= 0] = 0
        residual.eliminate_zeros()

        # 7. Find reachable partition from Source (Foreground)
        node_order, predecessors = breadth_first_order(residual, 0, directed=True)
        
        # Determine foreground pixels (strictly between 1 and N)
        foreground_nodes = node_order[(node_order > 0) & (node_order < V - 1)] - 1
        mask = np.zeros(N, dtype=np.uint8)
        mask[foreground_nodes] = 255
        mask = mask.reshape((H, W))

        # 8. Create cutout output and save
        reconstructed_rgb = all_colors.reshape((H, W, 3)).astype(np.uint8)
        reconstructed_bgr = cv.cvtColor(reconstructed_rgb, cv.COLOR_RGB2BGR)

        segmented_img = np.zeros_like(reconstructed_bgr)
        segmented_img[mask == 255] = reconstructed_bgr[mask == 255]

        output_path = "/Users/mbp/Desktop/output_image.png"
        cv.imwrite(output_path, segmented_img)
        print(f"[Segmentation] Saved segmented cutout to {output_path}")


class ThresholdingImageSegmentation(ImageSegmentation):
    def __init__(self):
        super().__init__()

    def segmentation(self):
        pass