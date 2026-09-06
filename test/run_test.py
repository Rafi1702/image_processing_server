import cv2 as cv
import numpy as np
from PIL import Image
from image_processor.image_segmentation import GraphCutImageSegmentation, SegmentationBoundaryPoint
from image_processor.graph_util import GraphBuilderFlatten
from data.datasource.implementation.image_data_source_opencv_impl import ImageDataSourcePilImpl

def main():
    matrix = [1,2,3,4,5,6,7,8]

    build_graph = GraphBuilderFlatten(image_width=4, image_height=2, image_source=matrix)

    print(build_graph.copy == [1, 2, 3, 4, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 0, 0, 0, 0, 0, 0])


    # image_path = "image_processor/roblox.png"
    # print(f"Loading image from {image_path}...")
    # ds = ImageDataSourcePilImpl()
    # img_data = ds.get_images(image_path)
    # W, H = img_data.width, img_data.height
    # print(f"Image dimensions: {W}x{H}")

    # # Generate precise scribble points on roblox.png
    # # Foreground points: Character body/head (center region: x=45%..55%, y=45%..55%)
    # fg_points_list = []
    # for y in range(int(H * 0.45), int(H * 0.58), 3):
    #     for x in range(int(W * 0.46), int(W * 0.54), 3):
    #         fg_points_list.append((x, y))

    # # Background points: canvas background (top-left & top-right outer canvas)
    # bg_points_list = []
    # # Top-left background stroke (x=5%..25%, y=5%..25%)
    # for y in range(int(H * 0.05), int(H * 0.20), 3):
    #     for x in range(int(W * 0.05), int(W * 0.20), 3):
    #         bg_points_list.append((x, y))

    # # Top-right background stroke (x=75%..95%, y=5%..20%)
    # for y in range(int(H * 0.05), int(H * 0.20), 3):
    #     for x in range(int(W * 0.75), int(W * 0.95), 3):
    #         bg_points_list.append((x, y))

    # fg_pts_set = {SegmentationBoundaryPoint(x, y) for x, y in fg_points_list}
    # bg_pts_set = {SegmentationBoundaryPoint(x, y) for x, y in bg_points_list}

    # print(f"FG points count: {len(fg_pts_set)}, BG points count: {len(bg_pts_set)}")

    # # 1. Create and save scribble visualization image to test/scribble_input.png
    # orig_img = cv.imread(image_path, cv.IMREAD_UNCHANGED)
    # if orig_img.shape[2] == 4:
    #     viz_img = orig_img.copy()
    # else:
    #     viz_img = cv.cvtColor(orig_img, cv.COLOR_BGR2BGRA)

    # # Draw FG scribbles (Red in BGRA: B=0, G=0, R=255, A=255)
    # for x, y in fg_points_list:
    #     cv.circle(viz_img, (x, y), 3, (0, 0, 255, 255), -1)

    # # Draw BG scribbles (Blue in BGRA: B=255, G=0, R=0, A=255)
    # for x, y in bg_points_list:
    #     cv.circle(viz_img, (x, y), 3, (255, 0, 0, 255), -1)

    # scribble_out_path = "test/scribble_input.png"
    # cv.imwrite(scribble_out_path, viz_img)
    # print(f"Saved scribble visualization image to: {scribble_out_path}")

    # # 2. Run GraphCutImageSegmentation
    # seg = GraphCutImageSegmentation(
    #     image_data=img_data,
    #     fg_boundary_points=fg_pts_set,
    #     bg_boundary_points=bg_pts_set
    # )
    # result_path = seg.segmentation()

    # # Move output to test/segmented_output.png
    # seg_img = cv.imread(result_path, cv.IMREAD_UNCHANGED)
    # test_seg_out_path = "test/segmented_output.png"
    # cv.imwrite(test_seg_out_path, seg_img)
    # print(f"Saved segmented output image to: {test_seg_out_path}")

if __name__ == "__main__":
    main()
