import cv2 as cv
import numpy as np
import sys
import random
import os
import matplotlib.pyplot as plt
from PIL import Image
from pillow_heif import register_heif_opener



window_size = (1000, 750)

def otsu_func(filename, finemame_anotadas, nome_arquivo):
    # Load image
    if filename.endswith('.heic') or filename.endswith('.HEIC'):
        register_heif_opener()
        image = Image.open(f'{filename}')
        img_original = image.convert('RGB')
        img_original = np.array(img_original)
        img_original = cv.cvtColor(img_original, cv.COLOR_RGB2BGR)
    else:
        img_original = cv.imread(f'{filename}')
        print(type(img_original))
    dims = img_original.shape

    grey_cropped_img, cropped_img = crop_img_foreground(img_original)
    grey_cropped_img = cv.GaussianBlur(grey_cropped_img, (5,5), 0)
    _, binary_image = cv.threshold(grey_cropped_img, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    # binary_image = cv.bitwise_not(binary_image)
    

    # print_grey_img(binary_image)
    num_labels, labels, centroids, img = get_connected_components(binary_image, cropped_img)
    # print_grey_img(img)

    img_original_anotada = label_connected_components(img, centroids, num_labels)

    img_original_anotada = add_label(img_original_anotada, num_labels, dims)
    cv.imwrite(f"{finemame_anotadas}/{nome_arquivo}_otsu.jpg", img_original_anotada)



            

    return

def get_connected_components(img, img_original):
    
    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(img, connectivity=8)

    # Define your area threshold
    min_area = 500  # Adjust based on your requirements

    # Create an output image to draw the filtered components
    output = np.zeros_like(img)

    # Loop through all components, skipping the background (label 0)
    for label in range(1, num_labels):  # Start from 1 to skip the background
        if stats[label, cv.CC_STAT_AREA] >= min_area:
            output[labels == label] = 255

    # Now, run connected components on the output image to get new labels
    new_num_labels, new_labels, new_stats, new_centroids = cv.connectedComponentsWithStats(output, connectivity=8)

    # Find contours
    contours, _ = cv.findContours(output, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # Draw contours on the original image
    img_with_borders = img_original.copy()
    # cv.drawContours(img_with_borders, contours, -1, (255, 0, 0), 1)  # Green borders

    return new_num_labels, new_labels, new_centroids, img_with_borders


def label_connected_components(img: np.array, centroids: np.array, num_labels: int) -> np.array:
    # Define the color for the text (green in BGR format)
    color = (0, 255, 0)  # BGR for green

    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5  # Size of the font
    thickness = 1  # Thickness of the font

    # Loop through the centroids and draw the label at each centroid
    for i in range(1, num_labels):  # Start from 1 to skip the background
        # Centroid coordinates are given as (column, row), which corresponds to (x, y)
        x = int(centroids[i][0])
        y = int(centroids[i][1])
        
        # Get the size of the text box
        text = str(i)
        text_size = cv.getTextSize(text, font, font_scale, thickness)[0]
        
        # Calculate the center position
        text_x = x - text_size[0] // 2
        text_y = y + text_size[1] // 2
        
        # Put the text on the image
        cv.putText(img, text, (text_x, text_y), font, font_scale, color, thickness, cv.LINE_AA)

    return img

def add_label(img: np.array, num_labels: int, dims: np.array):
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 5  # Size of the font
    color = (255, 255, 255)  # White color text
    thickness = 2  # Thickness of the font
    position = (30, img.shape[0] - 30)  # Bottom left corner of the image
    text = f' {num_labels}'

    # Put the text on the image
    cv.putText(img, text, position, font, font_scale, color, thickness, cv.LINE_AA)

    return img


def print_grey_img(img):
    plt.imshow(img, cmap='gray')
    plt.axis('off')  # Hide the axis
    plt.show()


#crops image and homogenizes the background
def crop_img_foreground(img):
    radius_proportion = 0.98
    # Apply a binary threshold to get a binary image
    gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray_image[gray_image < 50] = 255
    _, binary_image = cv.threshold(gray_image, 254, 255, cv.THRESH_BINARY_INV)

    # Find connected components
    num_labels, labels_im = cv.connectedComponents(binary_image)

    # Find the largest connected component (excluding the background)
    largest_component = 1 + np.argmax(np.bincount(labels_im.flat)[1:])

    # Create a mask for the largest component
    mask = np.uint8(labels_im == largest_component) * 255

    # Find the center and radius of the largest component
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv.contourArea)
    (x, y), radius = cv.minEnclosingCircle(largest_contour)

    # Create a circular mask with a slightly smaller radius
    mask_circular = np.zeros_like(mask)
    cv.circle(mask_circular, (int(x), int(y)), int(radius * radius_proportion), 255, -1)

    # Apply the circular mask to the original image
    cropped_image = cv.bitwise_and(gray_image, gray_image, mask=mask_circular)
    cropped_image[cropped_image < 50] = 255

    # Find the bounding box of the circular mask
    x, y, w, h = cv.boundingRect(mask_circular)

    # Crop the image to the bounding box
    cropped_image = cropped_image[y:y+h, x:x+w]

    hist = cv.calcHist([cropped_image], [0], None, [256], [0, 256]).flatten()
    sorted_indices = np.argsort(hist)[::-1]

    #selects the color the background should become
    new_backgroundcolor = sorted_indices[0]
    if(new_backgroundcolor == 255):
        new_backgroundcolor = sorted_indices[1]
    
    #sets background to most common color to otsu can determine best threshold
    cropped_image[cropped_image == 255] = new_backgroundcolor

    cropped_color_img = img[y:y+h, x:x+w]
    return cropped_image, cropped_color_img


def mkdir(new_directory_name):
    current_directory = os.getcwd()
    path = os.path.join(current_directory, new_directory_name)

    try:
        # Create the directory
        os.makedirs(path, exist_ok=True)  # 'exist_ok=True' will not raise an error if the directory already exists
        print(f"Directory '{new_directory_name}' created at '{path}'")
    except OSError as error:
        print(f"Creation of the directory '{new_directory_name}' failed")
        print(error)





def label_connected_components(img: np.array, centroids: np.array, num_labels: int) -> np.array:
    # Define the color for the text (green in BGR format)
    color = (0, 255, 0)  # BGR for green

    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5  # Size of the font
    thickness = 1  # Thickness of the font

    # Loop through the centroids and draw the label at each centroid
    for i in range(1, num_labels):  # Start from 1 to skip the background
        # Centroid coordinates are given as (column, row), which corresponds to (x, y)
        x = int(centroids[i][0])
        y = int(centroids[i][1])
        
        # Get the size of the text box
        text = str(i)
        text_size = cv.getTextSize(text, font, font_scale, thickness)[0]
        
        # Calculate the center position
        text_x = x - text_size[0] // 2
        text_y = y + text_size[1] // 2
        
        # Put the text on the image
        cv.putText(img, text, (text_x, text_y), font, font_scale, color, thickness, cv.LINE_AA)

    return img





def print_hist(img):
    hist = cv.calcHist([img], [0], None, [256], [0, 256])
    # Plot the histogram
    plt.figure()
    plt.title("Grayscale Histogram")
    plt.xlabel("Bins")
    plt.ylabel("# of Pixels")
    plt.plot(hist)
    plt.xlim([0, 256])
    plt.show()

