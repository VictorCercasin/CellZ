from pathlib import Path
from .config import INPUT_DIR, OUTPUT_DIR, SUPPORTED_FORMATS, IMAGE_EXTENSIONS

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
        
        # Create corresponding output path
        output_img_path = output_dir / relative_path
        
        # Only process if output doesn't exist
        if not output_img_path.exists():
            images_to_analyze.append(input_img)
    
    # print(f"Found {len(input_images)} total images, {len(images_to_analyze)} new to process")
    return images_to_analyze



def setup_directories():
    """Creates input and output directories if they don't exist"""
    input_path = Path.cwd() / INPUT_DIR
    output_path = Path.cwd() / OUTPUT_DIR
    
    input_path.mkdir(exist_ok=True)
    output_path.mkdir(exist_ok=True)
    
    print(f"Directories set up: {INPUT_DIR}, {OUTPUT_DIR}")