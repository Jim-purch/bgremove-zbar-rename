# bgremove-zbar-rename

一个基于 AI 的样品图片处理工具，支持图片主体提取、尺寸压缩、背景添加和批量格式转换。

## 功能特性

- **01. 提取图片主体** - 使用 BriaAI 模型智能去除图片背景，提取主体
- **02. 压缩尺寸并添加背景** - 对提取后的主体进行尺寸压缩，并添加指定背景
- **03. 批量更改上传格式** - 将处理后的图片批量转换为适合上传的格式

## 环境要求

- Python 3.8+
- PyTorch
- Transformers
- Pillow (PIL)
- NumPy
- tkinter (Python 标准库)

## 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/Jim-purch/bgremove-zbar-rename.git
cd bgremove-zbar-rename
```

2. 安装依赖：
```bash
pip install torch torchvision transformers pillow numpy
```

## 使用方法

1. 运行主程序：
```bash
python background_remover.py
```

2. 在图形界面中：
   - 选择输入文件夹（包含待处理的原始图片）
   - 选择输出文件夹（处理后的图片将保存到此目录）
   - 设置最大图片尺寸
   - 点击 **01. 开始提取图片中的主体** 按钮开始处理

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

## 注意事项

- 模型文件 (`.bin`) 未包含在仓库中，首次运行会自动从 Hugging Face 下载
- 输入输出文件夹不能相同
- 支持的图片格式: PNG, JPG, JPEG

## 许可证

MIT License
