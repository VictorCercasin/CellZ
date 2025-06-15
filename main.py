import os

from pathlib import Path
from src import (get_img_list, setup_directories, crop_image, show_images_fitted, read_image, remove_background
                 , find_cell_centroids, label_image)
from time import sleep

import cv2 as cv


def main():
    # sets up the necessary direcotries
    setup_directories()
    # Grab a list of all the image files from, including absolute path
    img_path_list = get_img_list('imagens')
    print(f"Foram encontradas {len(img_path_list)} imagens para análise")
    for index, img_path in enumerate(img_path_list):
        image = read_image(str(img_path))
        # if index < 0:
        #     continue
        image = crop_image(image)
        image = remove_background(image)
        centroids = find_cell_centroids(image)
        labeled_image = label_image(image, centroids)

        show_images_fitted([labeled_image])









if __name__ == "__main__":
    main()
