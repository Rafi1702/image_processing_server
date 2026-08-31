import numpy as np
import cv2

def compare_images(img1: np.ndarray, img2: np.ndarray):
    """
    Compares two image arrays and prints exact statistical metrics.
    """
    if img1.shape != img2.shape:
        print(f"[Mismatch] Shapes differ: {img1.shape} vs {img2.shape}")
        return

    # Check absolute binary identity
    is_identical = np.array_equal(img1, img2)
    print(f"Are images strictly identical? {is_identical}")

    # Compute absolute difference
    diff = np.abs(img1.astype(np.float64) - img2.astype(np.float64))
    
    total_pixels = img1.shape[0] * img1.shape[1]
    # Count pixels where any channel changed
    changed_pixels = np.count_nonzero(diff.sum(axis=-1) if diff.ndim == 3 else diff)
    
    print(f"Total Pixels: {total_pixels}")
    print(f"Changed Pixels: {changed_pixels} ({(changed_pixels / total_pixels) * 100:.2f}%)")
    print(f"Max Difference: {diff.max():.4f}")
    print(f"Mean Absolute Difference: {diff.mean():.4f}")

    # Create visual difference map
    # Multiply difference to make subtle changes visible
    diff_visual = np.clip(diff * 5.0, 0, 255).astype(np.uint8)
    
    return diff_visual