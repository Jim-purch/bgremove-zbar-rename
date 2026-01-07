# bgremove-zbar-rename

An AI-powered sample image processing tool that supports subject extraction, size compression, background addition, and batch format conversion.

[中文版文档 (Chinese Version)](README_CN.md)

## Features

- **01. Extract Image Subject** - Intelligently remove image background and extract subjects using BriaAI model
- **02. Compress Size and Add Background** - Compress extracted subjects and add specified backgrounds
- **03. Batch Convert to Upload Format** - Batch convert processed images to upload-ready format

## Requirements

### Operating System
- Windows 10/11 (Recommended)

### Python Environment
- Python 3.8 or higher

### Python Dependencies
- **torch** - PyTorch deep learning framework
- **torchvision** - PyTorch computer vision library
- **transformers** - Hugging Face Transformers library (for loading AI models)
- **pillow** - Python image processing library (PIL)
- **numpy** - Numerical computing library
- **tkinter** - Python standard library GUI framework (usually installed with Python)

### External Software
- **ZBar** - Barcode recognition tool
  - Windows version download: https://sourceforge.net/projects/zbar/
  - Installation path: `C:\Program Files (x86)\ZBar\`
  - Ensure `zbarimg.exe` is located at `C:\Program Files (x86)\ZBar\bin\` after installation

## Installation

### 1. Install ZBar (Barcode Recognition Tool)
1. Download ZBar Windows installer
2. Run the installer with default installation path `C:\Program Files (x86)\ZBar\`
3. Verify installation: Check if `C:\Program Files (x86)\ZBar\bin\zbarimg.exe` exists

### 2. Clone the Repository
```bash
git clone https://github.com/Jim-purch/bgremove-zbar-rename.git
cd bgremove-zbar-rename
```

### 3. Install Python Dependencies
```bash
pip install torch torchvision transformers pillow numpy
```

**Note**: PyTorch installation may require selecting the appropriate version based on your CUDA version. Visit [PyTorch Official Website](https://pytorch.org/get-started/locally/) for installation commands.

### 4. Verify Model Files
Ensure the `models/briaai_rmbg/` directory contains the following model files:
- `config.json`
- `preprocessor_config.json`
- `pytorch_model.bin` (or other model weight files)
- `MyConfig.py`
- `MyPipe.py`
- `briarmbg.py`
- `utilities.py`

If model files are missing, the program will attempt to download them automatically from Hugging Face.

## Usage

### Run the Program
```bash
python background_remover.py
```

### Workflow

#### Step 01: Extract Image Subject
1. Select input folder (containing original images to process)
2. Select output folder (processed images will be saved here)
3. Set maximum image size (default: 2400 pixels)
4. Click **01. Start extracting image subject** button
5. The program will use AI model to automatically remove background and extract subjects, saving as PNG format
6. After processing, check and manually adjust image subjects if needed

#### Step 02: Compress Size and Add Background
1. Confirm that you have checked and manually adjusted the image subjects
2. Click **02.【After checking and manually adjusting image subjects】Compress size and add background** button
3. The program will:
   - Compress all PNG images to 700x700 pixels
   - Add three backgrounds (BAT, TMT, white) to each image
   - Copy original input images to output folder
   - Use ZBar to recognize barcodes in images
   - Create corresponding folders and move images based on barcode information
4. After processing, all images will be organized into subfolders by barcode

#### Step 03: Batch Convert to Upload Format
1. Ensure all images are organized in folders (under NewFolder directory)
2. Prepare a matching table TXT file with format: `OE Code=Sample Part Code` (one per line)
3. Click **03.【After organizing all images in folders】Batch convert to upload format** button
4. Select the matching table TXT file
5. The program will:
   - Create BAT, TMT, white subdirectories for each subfolder
   - Move images to corresponding subdirectories
   - Compress all images to 800x800 pixels
   - Create batch upload folder based on images in white directory
   - Rename images to `Sample Part Code-Number.jpg` format according to matching table
   - Generate `红T批量上传照片-8` folder under NewFolder directory
   - Record unmatched OE codes in error.txt

## Project Structure

```
bgremove-zbar-rename/
├── background_remover.py      # Main program entry
├── .gitignore                 # Git ignore configuration
├── models/
│   ├── background/            # Background image resources
│   │   ├── BAT.png
│   │   ├── TMT.jpg
│   │   └── white.png
│   └── briaai_rmbg/           # BriaAI background removal model
│       ├── MyConfig.py
│       ├── MyPipe.py
│       ├── briarmbg.py
│       ├── config.json
│       ├── preprocessor_config.json
│       └── utilities.py
```

## Tech Stack

- **Background Removal Model**: BriaAI/BRIAR-MBG (briaai/RMBG-1.4)
- **GUI Framework**: tkinter
- **Deep Learning Framework**: PyTorch
- **Image Processing**: Pillow, NumPy
- **Model Loading**: Hugging Face Transformers
- **Barcode Recognition**: ZBar
- **Concurrent Processing**: Python threading, concurrent.futures

## Notes

### Installation Notes
- **ZBar Installation Path**: The program defaults to `C:\Program Files (x86)\ZBar\bin\zbarimg.exe`. If installed elsewhere, modify the path in the code
- **PyTorch Version**: Recommend selecting appropriate PyTorch version based on your GPU CUDA version for better performance
- **Model Files**: On first run, if model files are missing, the program will attempt to download automatically from Hugging Face (requires internet connection)

### Usage Notes
- **Input/Output Folders Must Be Different**: The program will check and display an error if they are the same
- **Processing Order**: Must follow 01 → 02 → 03 sequence; proceed to next step only after completing the current one
- **Manual Check**: After Step 01, manually check and adjust image subjects to ensure extraction quality
- **Barcode Recognition**: Ensure barcodes in images are clearly visible, otherwise recognition may fail
- **Matching Table Format**: The matching table TXT file for Step 03 must use UTF-8 encoding with format `OE Code=Sample Part Code`

### Performance Optimization
- The program uses multi-threading to process multiple images simultaneously
- Barcode recognition uses thread pool, processing up to 6 images simultaneously
- Background removal model is cached in memory after loading to avoid repeated loading

### Supported Image Formats
- Input formats: PNG, JPG, JPEG
- Output formats: PNG (Step 01), JPG (Step 02 and 03)

### Common Issues
1. **Model Loading Failed**: Check network connection or manually download model files to `models/briaai_rmbg/` directory
2. **Barcode Recognition Failed**: Ensure ZBar is correctly installed and barcodes in images are clearly visible
3. **Slow Image Processing**: Consider using GPU version of PyTorch or reduce the number of simultaneously processed images

## License

MIT License
