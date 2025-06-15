from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, SUPPORTED_FORMATS, IMAGE_EXTENSIONS
import cv2 as cv



def save_processed_image(input_path, processed_image):
    """
    Save processed image to output directory with mirrored structure
    Converts all formats to .jpg for compatibility
    
    Args:
        input_path: Original image path (Path object)
        processed_image: Processed image with labels
    """
    # Calculate relative path from input directory
    input_dir = Path.cwd() / INPUT_DIR
    relative_path = input_path.relative_to(input_dir)
    
    # Create corresponding output path with .jpg extension
    output_dir = Path.cwd() / OUTPUT_DIR
    output_path = output_dir / relative_path
    output_path = output_path.with_suffix('.jpg')  # Convert all to .jpg
    
    # Create output subdirectory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as JPG with good quality
    success = cv.imwrite(str(output_path), processed_image, [cv.IMWRITE_JPEG_QUALITY, 100])
    
    # if success:
    #     print(f"Saved: {relative_path}")
    # else:
    #     print(f"Failed to save: {relative_path}")

def get_img_list(root=INPUT_DIR):
    current_dir = Path.cwd()
    input_dir = current_dir / INPUT_DIR
    output_dir = current_dir / OUTPUT_DIR
    
    if not input_dir.exists():
        print(f"Input directory {INPUT_DIR} not found")
        return []
    
    # Get all input images
    input_images = []
    for ext in IMAGE_EXTENSIONS:
        input_images.extend(input_dir.rglob(ext))
    
    # Filter out already processed images
    images_to_analyze = []
    for input_img in input_images:
        # Calculate relative path from input directory
        relative_path = input_img.relative_to(input_dir)
        
        # Create corresponding output path WITH .jpg extension
        output_img_path = output_dir / relative_path
        output_img_path = output_img_path.with_suffix('.jpg')  # Always check for .jpg
        
        # Only process if output doesn't exist
        if not output_img_path.exists():
            images_to_analyze.append(input_img)
    
    print(f"Encontradas {len(input_images)} imagens no total, {len(images_to_analyze)} novas para processar")
    return images_to_analyze



def setup_directories():
    """Creates input and output directories if they don't exist"""
    input_path = Path.cwd() / INPUT_DIR
    output_path = Path.cwd() / OUTPUT_DIR
    
    input_path.mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)
    
    print(f"Diretórios configurados: {INPUT_DIR}, {OUTPUT_DIR}")