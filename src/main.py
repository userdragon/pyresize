import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END
from PIL import Image
import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径，适配PyInstaller打包"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def select_files():
    file_paths = filedialog.askopenfilenames(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    if file_paths:
        add_files_to_list(file_paths)

def add_files_to_list(file_paths):
    """将文件路径添加到列表框中"""
    file_list.delete(0, END)
    for path in file_paths:
        file_list.insert(END, path)

def on_drop(event):
    """处理拖放事件"""
    try:
        # 解析拖放的文件路径
        data = event.data
        if data.startswith('{') and data.endswith('}'):
            paths = data[1:-1].split('} {')
        else:
            paths = data.split()
        
        # 过滤有效的图片文件
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        valid_paths = [p for p in paths if p.lower().endswith(valid_extensions)]
        
        if valid_paths:
            add_files_to_list(valid_paths)
        else:
            messagebox.showwarning("警告", "请拖放图片文件（支持jpg、png、bmp等格式）")
    except Exception as e:
        messagebox.showerror("错误", f"拖放处理失败: {str(e)}")

def update_images():
    selected_files = [file_list.get(i) for i in range(file_list.size())]
    if not selected_files:
        messagebox.showerror("错误", "请先选择图片文件")
        return

    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
    except ValueError:
        messagebox.showerror("错误", "请输入有效的宽度和高度")
        return

    target_dpi = (96, 96)
    success_count = 0
    error_files = []

    for file_path in selected_files:
        try:
            with Image.open(file_path) as img:
                img = img.resize((width, height))
                exif_dict = img.info.get('exif', b'')
                img.save(file_path, exif=exif_dict, dpi=target_dpi)
            success_count += 1
        except Exception as e:
            error_files.append(f"{file_path}: {str(e)}")

    result_msg = f"成功处理 {success_count} 个文件\n"
    if error_files:
        result_msg += f"处理失败 {len(error_files)} 个文件:\n" + "\n".join(error_files)
    messagebox.showinfo("处理结果", result_msg)

# 创建主窗口
root = tk.Tk()
root.title("批量修改图片尺寸")
root.geometry("600x400")

# 启用拖放功能（使用内置方法，适配性更好）
root.bind('<Drop>', on_drop)
root.bind('<DragEnter>', lambda e: e.accept())
root.bind('<DragOver>', lambda e: e.accept())

# 宽度输入
tk.Label(root, text="宽度:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
width_entry = tk.Entry(root)
width_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
width_entry.insert(0, "800")

# 高度输入
tk.Label(root, text="高度:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
height_entry = tk.Entry(root)
height_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
height_entry.insert(0, "600")

# 文件列表区域
tk.Label(root, text="选中的文件:").grid(row=3, column=0, padx=10, pady=5, sticky="ne")

file_frame = tk.Frame(root)
file_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")

scrollbar = Scrollbar(file_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

file_list = Listbox(file_frame, yscrollcommand=scrollbar.set, width=50, height=10)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=file_list.yview)

# 绑定列表框拖放事件
file_list.bind('<Drop>', on_drop)
file_list.bind('<DragEnter>', lambda e: e.accept())
file_list.bind('<DragOver>', lambda e: e.accept())

# 浏览按钮
file_button = tk.Button(root, text="浏览", command=select_files)
file_button.grid(row=3, column=2, padx=10, pady=5)

# 更新按钮
update_button = tk.Button(root, text="批量更新图片", command=update_images)
update_button.grid(row=4, column=0, columnspan=3, pady=10)

# 布局配置
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
    
