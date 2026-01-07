# bgremove-zbar-rename

一个基于 AI 的样品图片处理工具，支持图片主体提取、尺寸压缩、背景添加和批量格式转换。

## 功能特性

- **01. 提取图片主体** - 使用 BriaAI 模型智能去除图片背景，提取主体
- **02. 压缩尺寸并添加背景** - 对提取后的主体进行尺寸压缩，并添加指定背景
- **03. 批量更改上传格式** - 将处理后的图片批量转换为适合上传的格式

## 环境要求

### 操作系统
- Windows 10/11（推荐）

### Python 环境
- Python 3.8 或更高版本

### Python 依赖库
- **torch** - PyTorch 深度学习框架
- **torchvision** - PyTorch 计算机视觉库
- **transformers** - Hugging Face Transformers 库（用于加载 AI 模型）
- **pillow** - Python 图像处理库 (PIL)
- **numpy** - 数值计算库
- **tkinter** - Python 标准库 GUI 框架（通常随 Python 安装）

### 外部软件
- **ZBar** - 条形码识别工具
  - Windows 版本下载地址：https://sourceforge.net/projects/zbar/
  - 安装路径：`C:\Program Files (x86)\ZBar\`
  - 确保安装后 `zbarimg.exe` 位于 `C:\Program Files (x86)\ZBar\bin\` 目录

## 安装步骤

### 1. 安装 ZBar（条形码识别工具）
1. 下载 ZBar Windows 安装包
2. 运行安装程序，默认安装路径为 `C:\Program Files (x86)\ZBar\`
3. 验证安装：检查 `C:\Program Files (x86)\ZBar\bin\zbarimg.exe` 是否存在

### 2. 克隆项目到本地
```bash
git clone https://github.com/Jim-purch/bgremove-zbar-rename.git
cd bgremove-zbar-rename
```

### 3. 安装 Python 依赖
```bash
pip install torch torchvision transformers pillow numpy
```

**注意**：PyTorch 安装可能需要根据你的 CUDA 版本选择合适的版本。访问 [PyTorch 官网](https://pytorch.org/get-started/locally/) 获取安装命令。

### 4. 验证模型文件
确保 `models/briaai_rmbg/` 目录包含以下模型文件：
- `config.json`
- `preprocessor_config.json`
- `pytorch_model.bin`（或其他模型权重文件）
- `MyConfig.py`
- `MyPipe.py`
- `briarmbg.py`
- `utilities.py`

如果模型文件缺失，程序会尝试从 Hugging Face 自动下载。

## 使用方法

### 运行程序
```bash
python background_remover.py
```

### 操作流程

#### 步骤 01：提取图片主体
1. 选择输入文件夹（包含待处理的原始图片）
2. 选择输出文件夹（处理后的图片将保存到此目录）
3. 设置最大图片尺寸（默认 2400 像素）
4. 点击 **01. 开始提取图片中的主体** 按钮
5. 程序将使用 AI 模型自动去除背景，提取图片主体并保存为 PNG 格式
6. 处理完成后，检查并手动调整图片主体（如有需要）

#### 步骤 02：压缩尺寸并添加背景
1. 确认已检查并手动调整好图片主体
2. 点击 **02.【检查并手动调整图片主体后】压缩尺寸并增加背景** 按钮
3. 程序将：
   - 将所有 PNG 图片压缩到 700x700 像素
   - 为每张图片添加三种背景（BAT、TMT、white）
   - 复制原始输入图片到输出文件夹
   - 使用 ZBar 识别图片中的条形码
   - 根据条形码信息创建对应文件夹并移动图片
4. 处理完成后，将所有图片按条形码分装到对应的子文件夹中

#### 步骤 03：批量更改为上传格式
1. 确保所有图片已按目录分装好（在 NewFolder 目录下）
2. 准备一个匹配表 TXT 文件，格式为：`OE号=样品配件编码`（每行一个）
3. 点击 **03.【将所有图片按目录分装好后】批量更改为上传格式** 按钮
4. 选择匹配表 TXT 文件
5. 程序将：
   - 为每个子文件夹创建 BAT、TMT、white 三个子目录
   - 将图片移动到对应的子目录
   - 将所有图片压缩到 800x800 像素
   - 根据 white 目录中的图片创建批量上传文件夹
   - 按照匹配表重命名图片为 `样品配件编码-序号.jpg` 格式
   - 在 NewFolder 目录下生成 `红T批量上传照片-8` 文件夹
   - 如果有无法匹配的 OE 号，会在 error.txt 中记录

## 项目结构

```
bgremove-zbar-rename/
├── background_remover.py      # 主程序入口
├── .gitignore                 # Git 忽略配置
├── models/
│   ├── background/            # 背景图片资源
│   │   ├── BAT.png
│   │   ├── TMT.jpg
│   │   └── white.png
│   └── briaai_rmbg/           # BriaAI 背景移除模型
│       ├── MyConfig.py
│       ├── MyPipe.py
│       ├── briarmbg.py
│       ├── config.json
│       ├── preprocessor_config.json
│       └── utilities.py
```

## 技术栈

- **背景移除模型**: BriaAI/BRIAR-MBG (briaai/RMBG-1.4)
- **GUI 框架**: tkinter
- **深度学习框架**: PyTorch
- **图像处理**: Pillow, NumPy
- **模型加载**: Hugging Face Transformers
- **条形码识别**: ZBar
- **并发处理**: Python threading, concurrent.futures

## 注意事项

### 安装注意事项
- **ZBar 安装路径**：程序默认使用 `C:\Program Files (x86)\ZBar\bin\zbarimg.exe`，如果安装在其他位置，需要修改代码中的路径
- **PyTorch 版本**：建议根据显卡 CUDA 版本选择合适的 PyTorch 版本，以提高处理速度
- **模型文件**：首次运行时，如果模型文件缺失，程序会尝试从 Hugging Face 自动下载（需要网络连接）

### 使用注意事项
- **输入输出文件夹不能相同**：程序会检查并提示错误
- **处理顺序**：必须按照 01 → 02 → 03 的顺序执行，每个步骤完成后才能进行下一步
- **手动检查**：步骤 01 完成后，建议手动检查并调整图片主体，确保提取质量
- **条形码识别**：确保图片中的条形码清晰可见，否则可能导致识别失败
- **匹配表格式**：步骤 03 的匹配表 TXT 文件必须使用 UTF-8 编码，格式为 `OE号=样品配件编码`

### 性能优化
- 程序使用多线程处理，可同时处理多张图片
- 条形码识别使用线程池，最多同时处理 6 张图片
- 背景移除模型加载后会缓存在内存中，避免重复加载

### 支持的图片格式
- 输入格式：PNG, JPG, JPEG
- 输出格式：PNG（步骤 01）、JPG（步骤 02 和 03）

### 常见问题
1. **模型加载失败**：检查网络连接或手动下载模型文件到 `models/briaai_rmbg/` 目录
2. **条形码识别失败**：确保 ZBar 已正确安装，且图片中的条形码清晰可见
3. **图片处理速度慢**：考虑使用 GPU 版本的 PyTorch，或减少同时处理的图片数量

## 许可证

MIT License
