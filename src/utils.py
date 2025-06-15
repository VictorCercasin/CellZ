
import cv2 as cv
import numpy as np
from time import sleep



def show_images_fitted(images, window_names=None, max_size=3000):
    """
    Display multiple images at the same time, each in its own window
    
    Args:
        images: List of images or single image
        window_names: List of window names or single name (optional)
        max_size: Maximum size for each image
    """
    # Handle single image case
    if not isinstance(images, list):
        images = [images]
    
    # Generate window names if not provided
    if window_names is None:
        window_names = [f"Image {i+1}" for i in range(len(images))]
    elif not isinstance(window_names, list):
        window_names = [window_names]
    
    # Ensure we have enough names
    while len(window_names) < len(images):
        window_names.append(f"Image {len(window_names)+1}")
    
    # Display each image
    for i, (image, name) in enumerate(zip(images, window_names)):
        height, width = image.shape[:2]
        
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv.resize(image, (new_width, new_height))
        else:
            resized = image
        
        # Position windows so they don't overlap
        cv.namedWindow(name, cv.WINDOW_NORMAL)
        cv.moveWindow(name, i , i )  # Offset each window
        cv.imshow(name, resized)
    
    # Wait for key press, then close all windows
    cv.waitKey(0)
    cv.destroyAllWindows()

