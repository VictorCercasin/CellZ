import cv2 as cv
import numpy as np
import pillow_heif
from  pathlib import Path
from PIL import Image
from time import sleep

from .utils import show_images_fitted
from .file_manager import save_processed_image

# Global variable to control saving of intermediate images
SAVE_POST_IMAGES = True  # Set to True to save all intermediate steps

def save_post_image(filename, image, quality=100):
    """
    Save image to imagens_post folder only if SAVE_POST_IMAGES is True
    
    Args:
        filename: Name of the file to save
        image: Image array to save
        quality: JPEG quality (default 100)
    """
    if not SAVE_POST_IMAGES:
        return
    
    # Create directory if it doesn't exist
    post_dir = Path('imagens_post')
    post_dir.mkdir(exist_ok=True)
    
    # Save the image
    cv.imwrite(str(post_dir / filename), image, [cv.IMWRITE_JPEG_QUALITY, quality])

def label_image(masked_image, centroids):
    """
    Add numbered labels to detected cells and total count in corner
    
    Args:
        masked_image: Original masked image
        centroids: List of (x, y) coordinates for cell centers
        
    Returns:
        Image with green numbered labels on each cell and total count
    """
    labeled_image = masked_image.copy()
    
    # Add numbered labels to each centroid
    for i, (cx, cy) in enumerate(centroids, 1):  # Start counting from 1
        # Add green text label
        cv.putText(labeled_image, str(i), (cx-5, cy+5),  # Slight offset for better visibility
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Green color, thickness 2
    
    # Add total count in the top-left corner
    total_count = len(centroids)
    count_text = f"Total: {total_count}"
    cv.putText(labeled_image, count_text, (30, 80),  # Top-left corner with margin
               cv.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)  # Slightly larger font for visibility
    
    return labeled_image

def find_cell_centroids(masked_image):
    """Find cell nuclei centroids using blue channel for masking, green channel for detection"""

    BACKGROUND_THRESHOLD_BIAS = 1
    FOREGROUND_THRESHOLD_BIAS = 1
    MIN_AREA = 20
    MAX_AREA = 200
    EXCLUSION_RADIUS = 60
    ITERATION_CUTOFF = 2
    
    # Extract channels
    blue_channel = masked_image[:, :, 0]
    green_channel = masked_image[:, :, 1]

    save_post_image('8 - blue channel.jpeg', blue_channel)
    
    # Sample mask (non-black areas from circle masking)
    sample_mask = cv.cvtColor(masked_image, cv.COLOR_BGR2GRAY) > 0
    
    # Stage 1: Use blue channel to remove background
    blue_masked = blue_channel.copy()
    blue_masked[~sample_mask] = 255
    
    # Aggressive threshold to remove background
    threshold_value, _ = cv.threshold(blue_masked, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    adjusted_threshold = threshold_value * BACKGROUND_THRESHOLD_BIAS
    _, cellular_mask = cv.threshold(blue_masked, adjusted_threshold, 255, cv.THRESH_BINARY_INV)

    save_post_image('9 - blue channel theshold.jpeg', cellular_mask)
    
    # Stage 2: Use green channel to find nuclei within cellular areas
    green_masked = green_channel.copy()
    green_masked[~sample_mask] = 128
    green_masked[cellular_mask == 0] = 128

    masked_image_removed_bg = masked_image.copy()
    masked_image_removed_bg[~sample_mask] = 128
    masked_image_removed_bg[cellular_mask == 0] = 128
    save_post_image('11 - original cells only.jpeg', masked_image_removed_bg)
    
    # Stage 2.5: Apply Gaussian blur to smooth the green channel
    green_blurred = cv.GaussianBlur(green_masked, (5, 5), 1.0)
    
    # Stage 3: Find dark nuclei with biased threshold
    cellular_areas = cellular_mask == 255
    
    # Get Otsu threshold and make it more restrictive
    otsu_threshold, _ = cv.threshold(green_blurred, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    
    # Bias the threshold to be more restrictive (only darkest areas)
    restrictive_threshold = otsu_threshold * FOREGROUND_THRESHOLD_BIAS
    
    # Apply the more restrictive threshold
    _, nuclei_binary = cv.threshold(green_blurred, restrictive_threshold, 255, cv.THRESH_BINARY_INV)
    
    save_post_image('12 - nucleus only.jpeg', nuclei_binary)

    masked_image_nuclei_only = masked_image_removed_bg.copy()
    masked_image_nuclei_only[nuclei_binary == 0] = 128

    save_post_image('12 - original nuclei only.jpeg', masked_image_nuclei_only)

    # Keep only cellular areas
    nuclei_binary[~cellular_areas] = 0
    
    # Stage 3.5: Clean up and separate touching nuclei
    # Remove small noise first
    kernel_small = np.ones((3,3), np.uint8)
    nuclei_binary = cv.morphologyEx(nuclei_binary, cv.MORPH_OPEN, kernel_small)
    
    save_post_image('13 - clean up noise.jpeg', nuclei_binary)
    
    # Erode to separate touching nuclei
    kernel_erode = np.ones((3,3), np.uint8)

    all_centroids = []
    used_mask = np.zeros_like(nuclei_binary)

    eroded_nuclei_binary = nuclei_binary
    for iteration in range(100):
       # Erode to separate more nuclei
        eroded_nuclei_binary = cv.erode(eroded_nuclei_binary, kernel_erode, iterations=5)

        # Create a color version for visualization with green dots
        eroded_with_dots = cv.cvtColor(eroded_nuclei_binary, cv.COLOR_GRAY2BGR)
        for cx, cy in all_centroids:  # Show ALL cells found so far
            cv.circle(eroded_with_dots, (cx, cy), 4, (0, 255, 0), 2)  # Green dots
        save_post_image(f'14 {iteration} - eroded.jpeg', eroded_with_dots)

        # Find connected components
        num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(eroded_nuclei_binary)

        good_nuclei_this_round = []

        for i in range(1, num_labels):
            area = stats[i, cv.CC_STAT_AREA]
            
            # Check if this nucleus is in the "sweet spot" size range
            if MIN_AREA <= area <= MAX_AREA:
                cx, cy = int(centroids[i][0]), int(centroids[i][1])
                
                # Make sure we haven't already detected this area
                if used_mask[cy, cx] == 0:
                    good_nuclei_this_round.append((cx, cy))
                    
                    if iteration > ITERATION_CUTOFF:
                        # Mark a circular area around this centroid as used
                        cv.circle(used_mask, (cx, cy), EXCLUSION_RADIUS, 255, -1)

        if iteration > ITERATION_CUTOFF:
            all_centroids.extend(good_nuclei_this_round)

        # Create visualization with ALL detected cells so far
        progress_image = masked_image.copy()  # Use original color image
        for cx, cy in all_centroids:  # Show ALL cells found so far
            cv.circle(progress_image, (cx, cy), 4, (0, 255, 0), 2)  # Green dots

        # # Add iteration info and count
        # cv.putText(progress_image, f"Iteration: {iteration}", (10, 30), 
        #         cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # cv.putText(progress_image, f"Cells found: {len(all_centroids)}", (10, 60), 
        #         cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # # Save the progress visualization
        # save_post_image(f'14 {iteration} - progress.jpg', progress_image)

        # Stop if no good nuclei found this round
        if len(good_nuclei_this_round) == 0:
            break
            
        # Dilate back partially
        eroded_nuclei_binary = cv.dilate(eroded_nuclei_binary, kernel_erode, iterations=3)

        # Create color version for dilated visualization
        dilated_with_dots = cv.cvtColor(eroded_nuclei_binary, cv.COLOR_GRAY2BGR)
        for cx, cy in all_centroids:  # Show ALL cells found so far
            cv.circle(dilated_with_dots, (cx, cy), 4, (0, 255, 0), 2)  # Green dots
        save_post_image(f'14 {iteration} - dilated.jpeg', dilated_with_dots)

    # Add iteration info and count
    cv.putText(progress_image, f"Iteration: {iteration}", (10, 30), 
            cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv.putText(progress_image, f"Cells found: {len(all_centroids)}", (10, 60), 
            cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Save the progress visualization
    save_post_image(f'15  finished.jpg', progress_image)

    all_centroids = remove_close_duplicates(all_centroids)
    
    return all_centroids

def remove_close_duplicates(centroids, min_distance=50):
    """Remove centroids that are too close to each other"""
    if len(centroids) <= 1:
        return centroids
    
    filtered = []
    for i, (x1, y1) in enumerate(centroids):
        is_duplicate = False
        for j, (x2, y2) in enumerate(filtered):
            distance = np.sqrt((x1-x2)**2 + (y1-y2)**2)
            if distance < min_distance:
                is_duplicate = True
                break
        if not is_duplicate:
            filtered.append((x1, y1))
    
    return filtered

def remove_background(image):
    TRESHOLD_BIAS = 1.4
    RADIUS_RATIO = 0.93
    
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    save_post_image('5 - greyscale.jpeg', gray)
    
    # Get Otsu threshold value and increase it by 20%
    threshold_value, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    # Adds a bias into the threshold to account for highlights on the background
    adjusted_threshold = threshold_value * TRESHOLD_BIAS  
    
    # Apply the adjusted threshold
    _, binary = cv.threshold(gray, adjusted_threshold, 255, cv.THRESH_BINARY)

    save_post_image('6 - theshold.jpeg', binary)

    # Uses dilation to help find the circle
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))  # Circular instead of square
    limit = 100
    for i in range(limit):
        new_binary = cv.dilate(binary, kernel, iterations=1)
        # Optional: check if no change occurred (convergence)
        if np.array_equal(binary, new_binary):
            print(f"Converged after {i} iterations")
            break
        binary = new_binary

    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get largest contour (should be your main white region)
        largest_contour = max(contours, key=cv.contourArea)
        
        # Find minimum enclosing circle
        (center_x, center_y), radius = cv.minEnclosingCircle(largest_contour)
        center = (int(center_x), int(center_y))
        # Compensates for radio increase during dilation process
        radius = int(radius * RADIUS_RATIO)
        
        # Create circular mask
        h, w = binary.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        cv.circle(mask, center, radius, 255, -1)  # Filled circle
        
        # Draw red circle outline on the original cropped image for visualization
        image_with_circle = image.copy()
        cv.circle(image_with_circle, center, radius, (0, 0, 255), 3)  # Red circle, thickness 3

        mask = np.zeros((h, w), dtype=np.uint8)
        cv.circle(mask, center, radius, 255, -1)

        # Set everything outside the circle to black
        result = image.copy()
        result[mask == 0] = [0, 0, 0]
        save_post_image('7 - bracked out bg.jpeg', result)
        
    return result

def crop_image(image):
    TRESHOLD_BIAS = 1.4
    
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # Get Otsu threshold value and increase it by 20%
    threshold_value, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    # Adds a bias into the threshold to account for highlights on the background
    adjusted_threshold = threshold_value * TRESHOLD_BIAS  
    
    # Apply the adjusted threshold
    _, binary = cv.threshold(gray, adjusted_threshold, 255, cv.THRESH_BINARY)
    
    # Find all contours
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # Filter out very small contours (noise)
    min_area = 1000
    large_contours = [c for c in contours if cv.contourArea(c) > min_area]
    
    if not large_contours:
        print("No large contours found!")
        return image
    
    # Combine all large contour points
    all_points = np.vstack(large_contours)
    
    # Get bounding box of all points combined
    x, y, w, h = cv.boundingRect(all_points)
    
    # Make it square and crop with boundary checks
    size = max(w, h)
    center_x, center_y = x + w//2, y + h//2
    left = max(0, center_x - size//2)  # Don't go below 0
    top = max(0, center_y - size//2)   # Don't go below 0
    
    # Make sure we don't exceed image boundaries
    img_height, img_width = image.shape[:2]
    right = min(img_width, left + size)
    bottom = min(img_height, top + size)
    
    # Crop with safe boundaries
    cropped_color = image[top:bottom, left:right]
    
    # Check if cropped image is valid
    if cropped_color.size == 0:
        print("Cropped image is empty!")
        return image
    
    save_post_image('1 - Original.jpeg', image)
    save_post_image('2 - greyscale.jpeg', gray)
    save_post_image('3 - threshold.jpeg', binary)
    save_post_image('4 - cropped.jpeg', cropped_color)
    
    return cropped_color

def read_image(image_path):
    """
    Read image from path, handling different formats including HEIC
    Returns numpy array (BGR format for OpenCV compatibility)
    """
    path = Path(image_path)
    extension = path.suffix.lower()
    
    if extension == '.heic':
        try:
            # Register HEIF opener with Pillow
            pillow_heif.register_heif_opener()
            
            # Open HEIC file
            pil_image = Image.open(image_path)
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert PIL to numpy array
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR (OpenCV format)
            image_bgr = cv.cvtColor(image_array, cv.COLOR_RGB2BGR)
            
            return image_bgr
            
        except ImportError:
            print("pillow-heif not installed. Install with: pip install pillow-heif")
            return None
        except Exception as e:
            print(f"Error reading HEIC file {image_path}: {e}")
            return None
    
    else:
        # Standard formats (jpg, png, jpeg, etc.)
        image = cv.imread(str(image_path))
        if image is None:
            print(f"Could not load image: {image_path}")
        return image