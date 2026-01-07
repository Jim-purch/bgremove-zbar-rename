import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import numpy as np
import torch
import torch.nn.functional as F
from torchvision.transforms.functional import normalize  # 解决normalize未定义的问题
from transformers import AutoModelForImageSegmentation
import threading
import concurrent.futures
import time
import subprocess

class BackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        master.title("样品图片处理工具")
        master.geometry("600x560")  # 调整窗口大小以容纳新的按钮

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.max_size = tk.IntVar(value=2400)

        tk.Label(master, text="输入文件夹:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(master, textvariable=self.input_folder, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(master, text="浏览", command=self.browse_input).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(master, text="输出文件夹:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(master, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(master, text="浏览", command=self.browse_output).grid(row=1, column=2, padx=10, pady=5)

        tk.Label(master, text="最大图片尺寸:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(master, textvariable=self.max_size, width=10).grid(row=2, column=1, sticky="w", padx=10, pady=5)

        self.start_button = tk.Button(master, text="01.开始提取图片中的主体", command=self.start_processing)
        self.start_button.grid(row=3, column=1, pady=10)

        self.stop_button = tk.Button(master, text="停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.grid(row=3, column=2, pady=10)

        self.compress_button = tk.Button(master, text="02.【检查并手动调整图片主体后】压缩尺寸并增加背景", command=self.start_compressing_thread)
        self.compress_button.grid(row=4, column=1, pady=10)

        self.batch_button = tk.Button(master, text="03.【将所有图片按目录分装好后】批量更改为上传格式", command=self.batch_process_images)
        self.batch_button.grid(row=5, column=1, pady=10)

        self.progress_label = tk.Label(master, text="")
        self.progress_label.grid(row=6, column=0, columnspan=3, pady=12)

        self.log_text = scrolledtext.ScrolledText(master, width=70, height=12)
        self.log_text.grid(row=7, column=0, columnspan=3, padx=10, pady=2)

        self.is_processing = False
        self.model = None

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def start_processing(self):
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()

        # 检查输入和输出文件夹是否相同
        if input_folder == output_folder:
            messagebox.showerror("错误", "输入文件夹和输出文件夹不能相同")
            return

        # 检查输出文件夹是否存在
        if not os.path.exists(output_folder):
            messagebox.showerror("错误", "输出文件夹不存在")
            return

        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        threading.Thread(target=self.process_images, daemon=True).start()

    def stop_processing(self):
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_label.config(text="处理已停止")

    def log_message(self, message):
        """将信息输出到文本框和命令行"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)  # 自动滚动到底部
        print(message)

    def process_images(self):
        input_folder = self.input_folder.get()
        output_folder = self.output_folder.get()

        self.progress_label.config(text="正在加载模型...")
        if self.model is None:
            try:
                model_path = os.path.join(os.getcwd(), "models", "briaai_rmbg")
                self.log_message(f"模型路径: {model_path}")
                self.model = AutoModelForImageSegmentation.from_pretrained(model_path, local_files_only=True, trust_remote_code=True)
                self.model.to("cpu")
                self.progress_label.config(text="模型加载成功")
                self.log_message("模型加载成功。")
            except Exception as e:
                messagebox.showerror("错误", f"模型加载失败: {e}")
                self.log_message(f"模型加载失败: {e}")
                return

        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total_images = len(image_files)

        for i, image_file in enumerate(image_files, 1):
            if not self.is_processing:
                break

            self.progress_label.config(text=f"正在处理图片 {i}/{total_images}: {image_file}")
            self.log_message(f"正在处理图片 {i}/{total_images}: {image_file}")

            input_path = os.path.join(input_folder, image_file)
            output_path = os.path.join(output_folder, os.path.splitext(image_file)[0] + '.png')

            try:
                self.process_single_image(input_path, output_path)
            except Exception as e:
                self.log_message(f"处理图片 {image_file} 时出错: {str(e)}")

        self.progress_label.config(text="处理完成")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_processing = False
        messagebox.showinfo("完成", "01. 提取图片主体处理完成。")

    def process_single_image(self, input_path, output_path):
        with Image.open(input_path) as img:
            img = self.resize_image(img, self.max_size.get())
            orig_im = np.array(img)

        orig_im_size = orig_im.shape[0:2]
        image = self.preprocess_image(orig_im, [1024, 1024]).to("cpu")

        with torch.no_grad():
            result = self.model(image)

        result_image = self.postprocess_image(result[0][0], orig_im_size)

        pil_im = Image.fromarray(result_image)
        no_bg_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
        no_bg_image.paste(img, mask=pil_im)
        
        # 使用PIL进行自动裁剪透明边界（替代wand的trim()）
        bbox = no_bg_image.getbbox()
        if bbox:
            no_bg_image = no_bg_image.crop(bbox)
        
        no_bg_image.save(output_path, 'PNG')

    def start_compressing_thread(self):
        """通过线程执行压缩背景操作，防止 GUI 卡死"""
        threading.Thread(target=self.compress_and_add_background, daemon=True).start()

    def compress_and_add_background(self):
        confirm = messagebox.askyesno("确认", "请确认是否已调整并剪裁图片主体。")
        if not confirm:
            return

        output_folder = self.output_folder.get()
        input_folder = self.input_folder.get()
        if not output_folder or not input_folder:
            messagebox.showerror("错误", "请选择输入和输出文件夹")
            return

        try:
            self.progress_label.config(text="正在压缩图片...")
            self.log_message("正在压缩图片...")

            # 使用PIL批量缩放图片（替代mogrify命令）
            resized_count = self.resize_images_in_folder(output_folder, 700)
            self.log_message(f"图片压缩完成，共缩放 {resized_count} 张图片")

            backgrounds = {
                "TMT": os.path.join(os.getcwd(), "models", "background", "TMT.jpg"),
                "BAT": os.path.join(os.getcwd(), "models", "background", "BAT.png"),
                "white": os.path.join(os.getcwd(), "models", "background", "white.png")
            }

            for img_file in os.listdir(output_folder):
                if img_file.lower().endswith('.png'):
                    base_name = os.path.splitext(img_file)[0]
                    img_path = os.path.join(output_folder, img_file)

                    for suffix, bg_path in backgrounds.items():
                        output_image = os.path.join(output_folder, f"{base_name}.{suffix}.jpg")
                        # 使用PIL进行图片合成（避免Windows命令行转义问题）
                        self.composite_image_on_background(bg_path, img_path, output_image)

            for img_file in os.listdir(output_folder):
                if img_file.lower().endswith('.png'):
                    os.remove(os.path.join(output_folder, img_file))

            self.copy_input_to_output(input_folder, output_folder)
            self.run_barcode_processing(output_folder)

            messagebox.showinfo("完成", "压缩增加背景执行完成。")
            self.progress_label.config(text="压缩增加背景执行完成。")
            self.log_message("压缩增加背景执行完成。")
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            self.log_message(f"处理失败: {str(e)}")

    def copy_input_to_output(self, input_folder, output_folder):
        try:
            for file_name in os.listdir(input_folder):
                full_file_name = os.path.join(input_folder, file_name)
                if os.path.isfile(full_file_name):
                    shutil.copy(full_file_name, output_folder)
            self.log_message("输入文件夹中的图片已复制到输出文件夹。")
        except Exception as e:
            self.log_message(f"复制文件时出错: {e}")

    def run_barcode_processing(self, output_folder):
        self.log_message("开始处理条形码识别...")

        def decode_barcode(image_path):
            zbarimg_path = r"C:\Program Files (x86)\ZBar\bin\zbarimg.exe"
            try:
                result = subprocess.run([zbarimg_path, image_path], capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
                output = result.stdout.strip()
                if output:
                    barcode_data = output.split(":")[-1].strip()
                    # 如果包含'/'或'\'，仅使用其后的部分
                    if '/' in barcode_data or '\\' in barcode_data:
                        barcode_data = barcode_data.split('/')[-1].split('\\')[-1]
                    return barcode_data
            except subprocess.TimeoutExpired:
                self.log_message(f"条形码识别超时: {image_path}")
            except Exception as e:
                self.log_message(f"识别条形码时出错: {e}")
            return None

        def create_folder_and_delete_image(image_path, barcode_data, new_folder_base_path):
            if barcode_data:
                folder_name = os.path.join(new_folder_base_path, barcode_data)
                try:
                    if not os.path.exists(folder_name):
                        os.mkdir(folder_name)
                    os.remove(image_path)
                    self.log_message(f"已删除图片: {image_path}，新建文件夹: {folder_name}")
                except Exception as e:
                    self.log_message(f"新建文件夹 '{folder_name}' 失败: {e}")
            else:
                self.log_message(f"未找到条形码信息: {image_path}")

            # 每次创建文件夹后等待 1 秒
            time.sleep(1)

        def get_images_sorted_by_name(folder_path):
            images = [f for f in os.listdir(folder_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')) and 'white' not in f.lower()]
            images.sort(key=lambda x: x.lower())
            return images

        folder_path = output_folder
        new_folder_base_path = os.path.join(folder_path, "NewFolder")

        if not os.path.exists(new_folder_base_path):
            os.mkdir(new_folder_base_path)

        images = get_images_sorted_by_name(folder_path)
        total_images = len(images)
        self.log_message(f"找到 {total_images} 张图片。")

        max_workers = min(6, os.cpu_count() or 1)
        barcode_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(decode_barcode, os.path.join(folder_path, img)): img for img in images}
            completed_count = 0
            for future in concurrent.futures.as_completed(futures):
                completed_count += 1
                self.progress_label.config(text=f"已处理 {completed_count}/{total_images} 张图片")
                try:
                    result = future.result()
                    if result is not None:
                        barcode_results.append((futures[future], result))
                except Exception as e:
                    self.log_message(f"条形码识别异常: {e}")

        barcode_results.sort(key=lambda x: x[0].lower())  # 按图片名称排序

        for image_name, barcode_data in barcode_results:
            image_path = os.path.join(folder_path, image_name)
            create_folder_and_delete_image(image_path, barcode_data, new_folder_base_path)

    def batch_process_images(self):
        """03. 批量处理 NewFolder 目录中的子文件夹图片"""
        output_folder = self.output_folder.get()
        new_folder_path = os.path.join(output_folder, "NewFolder")

        if not os.path.exists(new_folder_path):
            messagebox.showerror("错误", "NewFolder 文件夹不存在")
            return

        match_file = filedialog.askopenfilename(title="03.选择样品配件编码的匹配表", filetypes=[("Text files", "*.txt")])
        if not match_file:
            messagebox.showerror("错误", "请选择将OE号转换为样品配件编码的匹配表TXT文件")
            return

        self.progress_label.config(text="开始批量处理图片...")
        self.log_message("开始批量处理 NewFolder 中的图片...")

        # 读取匹配表
        match_table = {}
        with open(match_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('=')
                if len(parts) == 2:
                    oe_code, match_code = parts
                    match_table[oe_code.strip()] = match_code.strip()

        error_file_path = os.path.join(new_folder_path, "error.txt")

        # 遍历 NewFolder 目录中的每个子文件夹
        for subfolder_name in os.listdir(new_folder_path):
            subfolder_path = os.path.join(new_folder_path, subfolder_name)
            if os.path.isdir(subfolder_path):
                # 为每个子文件夹创建 BAT、TMT、white 目录
                for category in ["BAT", "TMT", "white"]:
                    category_folder = os.path.join(subfolder_path, category)
                    if not os.path.exists(category_folder):
                        os.mkdir(category_folder)

                # 移动图片到对应的目录
                for image_file in os.listdir(subfolder_path):
                    image_path = os.path.join(subfolder_path, image_file)
                    if os.path.isfile(image_path):
                        if "BAT" in image_file:
                            shutil.move(image_path, os.path.join(subfolder_path, "BAT", image_file))
                            self.resize_image_to_800(os.path.join(subfolder_path, "BAT", image_file))  # 压缩到800x800
                        elif "TMT" in image_file:
                            shutil.move(image_path, os.path.join(subfolder_path, "TMT", image_file))
                            self.resize_image_to_800(os.path.join(subfolder_path, "TMT", image_file))  # 压缩到800x800
                        elif "white" in image_file:
                            shutil.move(image_path, os.path.join(subfolder_path, "white", image_file))

        # 创建红T批量上传照片-8 文件夹
        batch_folder = os.path.join(new_folder_path, "红T批量上传照片-8")
        if os.path.exists(batch_folder):
            shutil.rmtree(batch_folder)
        os.mkdir(batch_folder)

        # 执行文件重命名和复制操作
        for subfolder_name in os.listdir(new_folder_path):
            if subfolder_name != "红T批量上传照片-8":
                subfolder_path = os.path.join(new_folder_path, subfolder_name)
                oe_code = subfolder_name

                match_code = match_table.get(oe_code)
                if not match_code:
                    with open(error_file_path, 'a', encoding='utf-8') as error_file:
                        error_file.write(f"Error: No match code found for folder '{oe_code}'\n")
                    continue

                white_folder = os.path.join(subfolder_path, "white")
                if not os.path.exists(white_folder):
                    self.log_message(f"Warning: No 'white' subfolder found in '{subfolder_name}'")
                    continue

                files = sorted(
                    [f for f in os.listdir(white_folder) if f.lower().endswith('.jpg')],
                    key=lambda f: os.path.getmtime(os.path.join(white_folder, f)),
                    reverse=True
                )

                # 重命名并复制图片
                for counter, file_name in enumerate(files, start=1):
                    file_path = os.path.join(white_folder, file_name)
                    new_file_name = f"{match_code}-{counter}.jpg"
                    shutil.copy(file_path, os.path.join(batch_folder, new_file_name))

        # 读取并显示 error.txt 的内容到日志框中
        if os.path.exists(error_file_path):
            with open(error_file_path, 'r', encoding='utf-8') as error_file:
                error_content = error_file.read()
                if error_content:
                    self.log_message(f"错误日志:\n{error_content}")
        else:
            self.log_message("没有错误发生。")

        self.progress_label.config(text="批量处理完成")
        self.log_message("批量处理完成。")

    def resize_image_to_800(self, image_path):
        """调整图片大小到800x800"""
        try:
            with Image.open(image_path) as img:
                img = img.resize((800, 800), Image.LANCZOS)
                img.save(image_path)
                self.log_message(f"图片已调整为800x800: {image_path}")
        except Exception as e:
            self.log_message(f"调整图片大小时出错: {e}")

    @staticmethod
    def composite_image_on_background(bg_path, img_path, output_path, target_size=700):
        """使用PIL将PNG图片居中合成到背景图上
        
        Args:
            bg_path: 背景图片路径
            img_path: 前景PNG图片路径（带透明通道）
            output_path: 输出图片路径
            target_size: 目标尺寸，前景图片会被缩放到这个范围内
        """
        # 打开背景图片
        background = Image.open(bg_path).convert('RGBA')
        bg_width, bg_height = background.size
        
        # 打开前景图片（PNG带透明通道）
        foreground = Image.open(img_path).convert('RGBA')
        fg_width, fg_height = foreground.size
        
        # 缩放前景图片到目标尺寸（保持宽高比）
        if fg_width > target_size or fg_height > target_size:
            ratio = min(target_size / fg_width, target_size / fg_height)
            new_width = int(fg_width * ratio)
            new_height = int(fg_height * ratio)
            foreground = foreground.resize((new_width, new_height), Image.LANCZOS)
            fg_width, fg_height = foreground.size
        
        # 计算居中位置
        x = (bg_width - fg_width) // 2
        y = (bg_height - fg_height) // 2
        
        # 合成图片
        background.paste(foreground, (x, y), foreground)
        
        # 转换为RGB并保存为JPG
        result = background.convert('RGB')
        result.save(output_path, 'JPEG', quality=95)
    
    @staticmethod
    def resize_image(image, max_size):
        width, height = image.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            return image.resize(new_size, Image.LANCZOS)
        return image
    
    @staticmethod
    def resize_images_in_folder(folder_path, max_size=700):
        """使用PIL批量缩放文件夹中的所有PNG图片
        
        Args:
            folder_path: 文件夹路径
            max_size: 最大尺寸（宽和高都不超过这个值）
        
        Returns:
            处理的图片数量
        """
        count = 0
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.png'):
                file_path = os.path.join(folder_path, filename)
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                        # 只有当图片尺寸超过最大值时才缩放
                        if width > max_size or height > max_size:
                            ratio = min(max_size / width, max_size / height)
                            new_size = (int(width * ratio), int(height * ratio))
                            resized = img.resize(new_size, Image.LANCZOS)
                            resized.save(file_path, 'PNG')
                            count += 1
                except Exception as e:
                    print(f"缩放图片 {filename} 时出错: {e}")
        return count

    @staticmethod
    def preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
        if len(im.shape) < 3:
            im = im[:, :, np.newaxis]
        im_tensor = torch.tensor(im, dtype=torch.float32).permute(2, 0, 1)
        im_tensor = F.interpolate(torch.unsqueeze(im_tensor, 0), size=model_input_size, mode='bilinear')
        image = torch.divide(im_tensor, 255.0)
        image = normalize(image, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
        return image

    @staticmethod
    def postprocess_image(result: torch.Tensor, im_size: list) -> np.ndarray:
        result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear'), 0)
        ma = torch.max(result)
        mi = torch.min(result)
        result = (result - mi) / (ma - mi)
        im_array = (result * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
        im_array = np.squeeze(im_array)
        return im_array

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
