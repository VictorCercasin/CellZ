import cv2 as cv
import numpy as np
import sys
import random
import os
import matplotlib.pyplot as plt

window_size = (1000, 750)

def watershed_func(filename, finemame_anotadas, nome_arquivo):
    
    img_original = cv.imread(f'{filename}')
    dims = img_original.shape

    grey_cropped_img, cropped_img = crop_img_foreground(img_original)

    _, binary_image = cv.threshold(grey_cropped_img, 0, 255, cv.THRESH_OTSU)
    
    _, _, _, img = get_connected_components(binary_image)

    centroids = get_watershed(img, cropped_img)

    img_original_anotada = label_connected_components(cropped_img, centroids, len(centroids))

    img_original_anotada = add_label(img_original_anotada, len(centroids), dims)
    cv.imwrite(f"{finemame_anotadas}/{nome_arquivo}_watershed.jpg", img_original_anotada)

    # img_original_anotada = label_connected_components(cropped_img, centroids, num_labels)

    # img_original_anotada = add_label(img_original_anotada, num_labels, dims)
    # cv.imwrite(f"{finemame_anotadas}/anotada_{filename}", img_original_anotada)



            

    return

def get_watershed(img, img_color):
    # kernel = np.ones((3,3), np.uint8)

    # sure_bg = cv.dilate(img, kernel, iterations = 7)
    # sure_bg = cv.erode(sure_bg, kernel, iterations = 2)
    # # sure_bg = cv.morphologyEx(img,cv.MORPH_OPEN, kernel, iterations=5)

    # sure_fg =  cv.distanceTransform(img, cv.DIST_L2, 3)
    # _, sure_fg = cv.threshold(sure_fg, 0.2*sure_fg.max(), 255, 0)
    # sure_fg = np.uint8(sure_fg)

    # unknown = cv.subtract(sure_bg, sure_fg)



    # Define the kernel
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))

    # Noise removal
    opening = cv.morphologyEx(img, cv.MORPH_OPEN, kernel, iterations=2)

    # Sure background area
    sure_bg = cv.dilate(opening, kernel, iterations=10)

    # dist_transform = cv.distanceTransform(sure_bg, cv.DIST_L2, 5)
    # _, sure_fg = cv.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
    sure_fg = cv.erode(opening, kernel, iterations=15)
    sure_fg = cv.dilate(sure_fg, kernel, iterations=10)
    # sure_fg = cv.erode(sure_fg, kernel, iterations=10)
    sure_fg = np.uint8(sure_fg)

    # Subtract sure_fg from sure_bg to get the unknown region
    unknown = cv.subtract(sure_bg, sure_fg)

    # Marker labelling
    _, markers = cv.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1

    # Mark the region of unknown with zero
    markers[unknown == 255] = 0


    # Apply watershed
    markers = cv.watershed(img_color, markers)
    # img_color[markers == -1] = [255, 0, 0]  # Mark the boundaries with red color

    # Extract centroids of labeled components
    positions = []
    for label in range(2, np.max(markers) + 1):  # labels start from 2
        mask = (markers == label).astype(np.uint8)
        moments = cv.moments(mask)
        if moments["m00"] != 0:
            centroid_x = int(moments["m10"] / moments["m00"])
            centroid_y = int(moments["m01"] / moments["m00"])
            positions.append((centroid_x, centroid_y))

    # Display the results


    # plt.subplot(1, 2, 1)
    # plt.title('Markers')
    # plt.imshow(markers, cmap='nipy_spectral')
    # plt.axis('off')

    # plt.subplot(1, 2, 2)
    # plt.title('Segmented Image')
    # plt.imshow(cv.cvtColor(img_color, cv.COLOR_BGR2RGB))
    # plt.axis('off')



    return positions

def get_connected_components(img: np.array):
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

    return new_num_labels, new_labels, new_centroids, output


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

def compare_2_img(img1, img2):
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.title('Image 1')
    plt.imshow(img1, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title('Image 2')
    plt.imshow(img2, cmap='gray')
    plt.axis('off')

    plt.show()

#crops image and homogenizes the background
def crop_img_foreground(img):
    # Convertendo para escala de cinza
    imagem_cinza = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Aplicando desfoque Gaussiano para reduzir ruído
    imagem_desfocada = cv.GaussianBlur(imagem_cinza, (5, 5), 0)
    
    # Usando o método de Otsu para encontrar o limiar automaticamente
    _, imagem_binaria = cv.threshold(imagem_desfocada, 0, 255, cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    
    # Operações morfológicas para melhorar a detecção
    kernel = np.ones((5,5), np.uint8)
    imagem_binaria = cv.morphologyEx(imagem_binaria, cv.MORPH_OPEN, kernel, iterations=2)
    
    # Encontrando componentes conectados
    num_rotulos, rotulos = cv.connectedComponents(imagem_binaria)
    
    # Encontrando o maior componente (excluindo o fundo)
    if num_rotulos > 1:
        maior_componente = 1 + np.argmax(np.bincount(rotulos.flat)[1:])
        # Criando máscara para o maior componente
        mascara = np.uint8(rotulos == maior_componente) * 255
    else:
        # Caso não haja componentes além do fundo
        return imagem_cinza, img
    
     # Converter BGR para RGB (OpenCV usa BGR, matplotlib usa RGB)
    img_rgb = cv.cvtColor(imagem_binaria, cv.COLOR_BGR2RGB)
    # Mostrar a imagem
    plt.figure(figsize=(10, 8))
    plt.imshow(img_rgb)
    plt.title(f'Imagem: ')
    plt.axis('off')  # Remove os eixos
    plt.show()
    sleep(99999)
    
    # Encontrando contornos
    contornos, _ = cv.findContours(mascara, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    if not contornos:
        return imagem_cinza, img
        
    maior_contorno = max(contornos, key=cv.contourArea)
    
    # Encontrando o círculo que melhor encaixa o contorno
    (x, y), raio = cv.minEnclosingCircle(maior_contorno)
    
    # Criando máscara circular com proporção ajustável do raio
    proporcao_raio = 0.98  # Ajustável conforme necessidade
    mascara_circular = np.zeros_like(mascara)
    cv.circle(mascara_circular, (int(x), int(y)), int(raio * proporcao_raio), 255, -1)
    
    # Encontrando a caixa delimitadora da máscara circular
    x, y, w, h = cv.boundingRect(mascara_circular)
    
    # Recortando a imagem original
    imagem_recortada_cor = img[y:y+h, x:x+w]
    
    # Recortando a imagem em escala de cinza e aplicando a máscara
    imagem_recortada_cinza = cv.bitwise_and(imagem_cinza, imagem_cinza, mask=mascara_circular)[y:y+h, x:x+w]
    
    # Criando uma máscara para a área fora do círculo na imagem recortada
    mascara_local = mascara_circular[y:y+h, x:x+w]
    
    # Determinando a cor de fundo usando histograma
    histograma = cv.calcHist([imagem_recortada_cinza], [0], mascara_local, [256], [0, 256]).flatten()
    indices_ordenados = np.argsort(histograma)[::-1]
    
    # Escolhendo a cor de fundo (evitando 255 se possível)
    cor_fundo = indices_ordenados[0]
    if cor_fundo == 255 and len(indices_ordenados) > 1:
        cor_fundo = indices_ordenados[1]
    
    # Definindo a área fora do círculo com a cor de fundo
    imagem_recortada_cinza[mascara_local == 0] = cor_fundo
    
    return imagem_recortada_cinza, imagem_recortada_cor








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



def get_connected_components(img: np.array):
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

    return new_num_labels, new_labels, new_centroids, output

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
