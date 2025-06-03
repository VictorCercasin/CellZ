import otsu
import watershed
import watershed_refactor
import os



def main():
    pasta_imagens = os.path.join(os.getcwd(), "imagens")
    pasta_watershed = 'imagensAnotadasWatershed'
    pasta_otsu = 'imagensAnotadasOtsu'
    
    # Criar a pasta de imagens se não existir
    if not os.path.exists(pasta_imagens):
        os.makedirs(pasta_imagens)
        print("A pasta 'imagens' foi criada. Por favor, adicione suas imagens nesta pasta.")
        return
    
    # Criar pastas de saída
    mkdir(pasta_otsu)
    mkdir(pasta_watershed)
    
    # Listar arquivos de imagem na pasta 'imagens'
    img_files = []
    for nome_arquivo in os.listdir(pasta_imagens):
        if nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.heic')):
            img_files.append(nome_arquivo)
    
    img_quantidade = len(img_files)
    
    if img_quantidade == 0:
        print("Não há imagens na pasta 'imagens'. Por favor, adicione alguns arquivos de imagem.")
        return
    
    for indice, nome_arquivo in enumerate(img_files):
        caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
        print(caminho_completo)
        print(f"{indice+1}/{img_quantidade}: {nome_arquivo}")
        otsu.otsu_func(caminho_completo, pasta_otsu, nome_arquivo)
        watershed.watershed_func(caminho_completo, pasta_watershed, nome_arquivo)
        # watershed_refactor.watershed()


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


if __name__ == "__main__":
    main()
