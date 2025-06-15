import os

from pathlib import Path
from src import (get_img_list, setup_directories, crop_image, show_images_fitted, read_image, remove_background
                 , find_cell_centroids, label_image, save_processed_image)
from time import sleep

import cv2 as cv


def main():
    # sets up the necessary direcotries
    setup_directories()
    # Grab a list of all the image files from, including absolute path
    img_path_list = get_img_list('imagens')
    print(f"{len(img_path_list)} imagens para processar")
    for index, img_path in enumerate(img_path_list):
        print(f"\nImagem {index+1}/{len(img_path_list)}: {img_path.name}")
        # Read image
        image = read_image(str(img_path))
        # Crop image into interest area
        cropped_image = crop_image(image)
        # Clears image background
        clean_image = remove_background(cropped_image)
        # Finds cell centroids
        centroids = find_cell_centroids(clean_image)
        # Label image with centroids and total
        labeled_image = label_image(clean_image, centroids)
        # Saves image in mirror directory
        save_processed_image(img_path, labeled_image)










if __name__ == "__main__":
    main()
