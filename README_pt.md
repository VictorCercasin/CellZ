# CellZ - Contador Automático de Células

**🇺🇸 English** | [🇧🇷 Português](README_pt.md)

> CellZ é uma ferramenta automatizada para contagem de células projetada para ajudar pesquisadores a analisar células de *Allium cepa* (cebola) em imagens de lâminas de microscópio. Utiliza técnicas avançadas de visão computacional para detectar e contar núcleos celulares individuais com alta precisão.

## Características
- ✅ Detecção e contagem automática de células usando Progressive Erosion Harvesting
- ✅ Análise de duplo canal para identificação robusta de núcleos
- ✅ Processamento em lote com preservação automática da estrutura de pastas
- ✅ Suporte para múltiplos formatos de imagem (JPEG, PNG, HEIC)
- ✅ Imagens de saída anotadas com células numeradas e contagem total
- ✅ Lida com células densamente agrupadas e sobrepostas

## Requisitos
- Python 3.8 ou superior
- Imagens tiradas da ocular do microscópio com área de visualização circular

## Instalação e Uso

1. **Instale as dependências:**
  ```bash
  pip install -r requirements.txt
  ```
2. **Execute o programa:**

```bash
python main.py
```
3. **Configuração da primeira execução:**
- O programa cria duas pastas: **IMAGENS** (entrada) e **IMAGENS ANOTADAS** (saída)
- Coloque suas imagens de microscópio na pasta **IMAGENS**
- Imagens processadas com contagem de células aparecem em **IMAGENS** 
- Imagens já processadas são automaticamente ignoradas


## Como Funciona
CellZ utiliza um algoritmo inovador de **Progressive Erosion Harvestingg** que:
1. Isola a área circular da amostra do fundo
2. Usa análise do canal azul para identificar regiões celulares
3. Usa análise do canal verde para detectar núcleos escuros dentro das células
4. Separa iterativamente núcleos em contato usando operações morfológicas
5. Valida detecções baseado em critérios de tamanho e forma

## Resultados de Exemplo


<table>
<tr>
<td><img src="assets/1745683144302.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683144302-anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Imavem Original</td>
<td align="center">Imagem Anotada</td>
</tr>
</table>

<table>
<tr>
<td><img src="assets/1745683144627.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683144627-anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Imavem Original</td>
<td align="center">Imagem Anotada</td>
</tr>
</table>

<table>
<tr>
<td><img src="assets/1745683145570.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683145570-anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Imavem Original</td>
<td align="center">Imagem Anotada</td>
</tr>
</table>




Criado por [Victor Hugo Cercasin](https://github.com/VictorCercasin/SortSorter).
Repositório do Projeto [GitHub](https://github.com/VictorCercasin/)