# CellZ - Automatic Cell Counter

**🇺🇸 English** | [🇧🇷 Português](README_pt.md)

> CellZ is an automated cell counting tool designed to help researchers analyze *Allium cepa* (onion) cells in microscope slide images. It uses advanced computer vision techniques to detect and count individual cell nuclei with high precision.

## Features
- ✅ Automatic cell detection and counting using Progressive Erosion Harvesting
- ✅ Dual-channel analysis for robust nucleus identification
- ✅ Batch processing with automatic folder structure preservation
- ✅ Support for multiple image formats (JPEG, PNG, HEIC)
- ✅ Annotated output images with numbered cells and total count
- ✅ Handles densely packed and overlapping cells

## Requirements
- Python 3.8 or higher
- Images taken from microscope eyepiece with circular viewing area

## Installation and Usage

1. Install Python

- Visit https://www.python.org/downloads/
- Download the latest version of Python
- Run the installation

<img src="assets/download_python.png" alt="python" width="400">

⚠️ IMPORTANT: During installation, make sure to check the "Add Python to PATH" or "Add Python to environment variables" option so Python works in the terminal.

<img src="assets/env_variables.png" alt="python" width="400">

2. Download CellZ
- At the top of the project page on [GitHub](https://github.com/VictorCercasin/CellZ), click the "Code" button and then "Download ZIP"
- Extract the file to a directory of your choice
- If you prefer, use git to clone the project

3. Install dependencies:
- Navigate to the CellZ folder in file explorer
- In the **address bar** (where the folder path is shown), delete the text, type `cmd` and press Enter

<img src="assets/cmd.png" alt="python" width="400">

- In the terminal that opens, run the command:

```bash
pip install -r requirements.txt
```

⚠️ If you get an error, try:
- `python -m pip install -r requirements.txt`
- Or restart your computer
- Or reinstall Python

- To run the program, simply type in the terminal:
```bash
python main.py
```

4. **First run and operation:**
- When run for the first time, the program creates two folders: **IMAGENS** (input) and **IMAGENS ANOTADAS** (output)
- Place your microscope images in the **IMAGENS** folder and run again
- Processed images with cell counts appear in the **IMAGENS ANOTADAS** directory
- Already processed images are automatically ignored

5. **Cleaning anomalies:**
- In some cases, certain regions of images may contain anomalies that make cell counting difficult:

<table>
<tr>
<td><img src="assets/1745683145534.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683145534anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Original Image</td>
<td align="center">Annotated Image</td>
</tr>
</table>

In these cases, it is recommended that the anomalous region be painted black before counting:

<table>
<tr>
<td><img src="assets/1745683145534 -.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683145534 -anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Image with painted anomalies</td>
<td align="center">Annotated Image</td>
</tr>
</table>

## How It Works
CellZ uses an innovative **Progressive Erosion Harvesting** algorithm that:
1. Isolates the circular sample area from the background
2. Uses blue channel analysis to identify cellular regions
3. Uses green channel analysis to detect dark nuclei within cells
4. Iteratively separates touching nuclei using morphological operations
5. Validates detections based on size and shape criteria

## Example Results

<table>
<tr>
<td><img src="assets/1745683144302.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683144302-anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Original Image</td>
<td align="center">Annotated Image</td>
</tr>
</table>

<table>
<tr>
<td><img src="assets/1745683144627.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683144627-anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Original Image</td>
<td align="center">Annotated Image</td>
</tr>
</table>

<table>
<tr>
<td><img src="assets/1745683145570.jpg" alt="Original" width="400"></td>
<td><img src="assets/1745683145570-anotada.jpg" alt="Processed" width="400"></td>
</tr>
<tr>
<td align="center">Original Image</td>
<td align="center">Annotated Image</td>
</tr>
</table>

Created by [Victor Hugo Cercasin](https://github.com/VictorCercasin/).
Project Repository [GitHub](https://github.com/VictorCercasin/CellZ).