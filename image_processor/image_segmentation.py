
from dataclasses import dataclass
from abc import ABC, abstractmethod
from image_processor.distribution_model import GaussianModel
import numpy as np
import cv2 as cv
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow, breadth_first_order
from image_processor.graph_util import remove_duplicates, GraphBuilderOpenCv
from .image_utils import compare_images

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
    def __init__(self, image_data):
        super().__init__() 
        self.graph =  graphBuilder = GraphBuilderOpenCv(
            image_width=image_data.width, 
            image_height=image_data.height, 
            source=image_data.image
        )

    
    def segmentation(self):
        pass


class GraphCutImageSegmentation(GraphBasedImageSegmentation):
    def __init__(self,image_data, fg_boundary_points: set[SegmentationBoundaryPoint], bg_boundary_points: set[SegmentationBoundaryPoint]):
        super().__init__(image_data=image_data) 
        
        self.fg_boundary_points = fg_boundary_points
        self.bg_boundary_points = bg_boundary_points

        self.fg_pixels = self.__get_pixels_from_boundary(fg_boundary_points, self.graph)
        self.bg_pixels = self.__get_pixels_from_boundary(bg_boundary_points, self.graph)
        self.all_colors = np.array([node.pixels for node in self.graph.nodes[1:-1]], dtype=np.float64)
        self.num_channels = self.all_colors.shape[1] if self.all_colors.ndim > 1 else 1

    
    @staticmethod
    def __get_pixels_from_boundary(boundary_points: set[SegmentationBoundaryPoint], graph):
        pixels = []
        for boundary_point in boundary_points:
            pixel_index = boundary_point.y * graph.image_width + boundary_point.x
            pixels.append(graph.nodes[pixel_index + 1].pixels)
            
        return pixels
    

    ## THIS METHOD IS TIGHT TO NUMPY
    def __construct_n_link(self, W: int, H:int):
        # Strip Alpha channel and normalize colors to [0, 1] for N-link diffs
        colors_rgb = self.all_colors[:, :3] if self.all_colors.ndim > 1 and self.all_colors.shape[1] > 3 else self.all_colors
        if colors_rgb.max() > 1.0:
            colors_rgb = colors_rgb / 255.0
            
        img_colors = colors_rgb.reshape((H, W, colors_rgb.shape[1]))

        def assembly_vectors(grid_h: int, grid_w: int, full_w: int, offset: int):
            y_indices, x_indices = np.ogrid[:grid_h, :grid_w]
            p1 = y_indices * full_w + x_indices
            p2 = p1 + offset
            u = p1.flatten() + 1  
            v = p2.flatten() + 1
            return u, v

        
        # Horizontal differences: (H, W-1, num_channels)
        diff_h = img_colors[:, :-1, :] - img_colors[:, 1:, :]
        sq_diff_h = np.sum(diff_h ** 2, axis=2)

        # Vertical differences: (H-1, W, num_channels)
        diff_v = img_colors[:-1, :, :] - img_colors[1:, :, :]
        sq_diff_v = np.sum(diff_v ** 2, axis=2)

        # Compute beta = 1 / (2 * mean(sq_diff))
        mean_sq_diff = (np.sum(sq_diff_h) + np.sum(sq_diff_v)) / (sq_diff_h.size + sq_diff_v.size)
        if mean_sq_diff == 0:
            mean_sq_diff = 1e-5
        beta = 1.0 / (2.0 * mean_sq_diff)

        gamma = 10.0
        w_h = gamma * np.exp(-beta * sq_diff_h)
        w_v = gamma * np.exp(-beta * sq_diff_v)


        u_h, v_h = assembly_vectors(grid_h=H, grid_w=W-1, full_w=W, offset=1)
        u_v, v_v = assembly_vectors(grid_h=H-1, grid_w=W, full_w=W, offset=W)
        weight_h = w_h.flatten()
        weight_v = w_v.flatten()

        u_neighbors = np.concatenate([u_h, v_h, u_v, v_v])
        v_neighbors = np.concatenate([v_h, u_h, v_v, u_v])
        weight_neighbors = np.concatenate([weight_h, weight_h, weight_v, weight_v])

        return u_neighbors, v_neighbors, weight_neighbors
    
    def __construct_t_link(self, W):
        LARGE_VAL = 1000.0
        fg_sets = self.fg_pixels
        bg_sets = self.bg_pixels

        print(f"Shape of fg_sets = {np.array(fg_sets).shape}")
        print(f"Shape of bg_sets = {np.array(bg_sets).shape}")

        # Model creation for object/fg and background/bg
        fg_distribution = GaussianModel(source=np.array(fg_sets, dtype=np.float64))
        bg_distribution = GaussianModel(source=np.array(bg_sets, dtype=np.float64))

        # Compute log likelihoods ln P(x | FG) and ln P(x | BG)
        log_p_fg = fg_distribution.log_likelihood(self.all_colors)
        log_p_bg = bg_distribution.log_likelihood(self.all_colors)

        # Log-Likelihood Ratio: delta = ln P(x|FG) - ln P(x|BG)
        diff_log = log_p_fg - log_p_bg

        # Scale factor to balance T-link likelihood ratio with N-link smoothness
        lambda_t = 5.0
        source_w = np.maximum(0, lambda_t * diff_log)
        sink_w = np.maximum(0, lambda_t * (-diff_log))

        fg_seed_indices = [pt.y * W + pt.x for pt in self.fg_boundary_points]
        bg_seed_indices = [pt.y * W + pt.x for pt in self.bg_boundary_points]

        source_w[fg_seed_indices] = LARGE_VAL
        sink_w[fg_seed_indices] = 0

        source_w[bg_seed_indices] = 0
        sink_w[bg_seed_indices] = LARGE_VAL

        return source_w, sink_w
    
    def segmentation(self):
        graph = self.graph.nodes
        all_colors = self.all_colors

        H, W = self.graph.image_height, self.graph.image_width
        N = H * W
        V = N + 2

        if len(self.fg_pixels) == 0 or len(self.bg_pixels) == 0:
            print("[Segmentation Error] Both foreground and background scribbles are required.")
            return
        

        source_w, sink_w = self.__construct_t_link(W)
        u_neighbors, v_neighbors, weight_neighbors = self.__construct_n_link(W= W, H= H)

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
        reconstructed_img = all_colors.reshape((H, W, self.num_channels)).astype(np.uint8)
        if self.num_channels == 4:
            reconstructed_bgr = cv.cvtColor(reconstructed_img, cv.COLOR_RGBA2BGRA)
        elif self.num_channels == 3:
            reconstructed_bgr = cv.cvtColor(reconstructed_img, cv.COLOR_RGB2BGR)
        else:
            reconstructed_bgr = reconstructed_img

        segmented_img = np.zeros_like(reconstructed_bgr)
        segmented_img[mask == 255] = reconstructed_bgr[mask == 255]

        output_path = "/Users/mbp/Desktop/output_image2.png"
        cv.imwrite(output_path, segmented_img)
        

        orig_converted = cv.cvtColor(
                self.graph.original_source.reshape((H, W, self.num_channels)).astype(np.uint8),
                cv.COLOR_RGBA2BGRA if self.num_channels == 4 else cv.COLOR_RGB2BGR
        ) if self.num_channels in (3, 4) else self.graph.original_source.reshape(segmented_img.shape)

        print(f"Compared Images Value: {compare_images(orig_converted, segmented_img)}")    
        
        return output_path


class ThresholdingImageSegmentation(ImageSegmentation):
    def __init__(self):
        super().__init__()

    def segmentation(self):
        pass