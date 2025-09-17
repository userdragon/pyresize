import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END
from PIL import Image
import os

def select_files():
    file_paths = filedialog.askopenfilenames(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    if file_paths:
        add_files_to_list(file_paths)

def add_files_to_list(file_paths):
    """将文件路径添加到列表框中"""
    # 清空现有列表
    file_list.delete(0, END)
    # 添加新文件
    for path in file_paths:
        file_list.insert(END, path)

def on_drag_enter(event):
    """处理拖拽进入事件"""
    event.widget.focus_set()
    # 检查拖拽的数据是否包含文件
    if event.data.startswith('{'):
        event.accept()
    else:
        event.ignore()

def on_drag_leave(event):
    """处理拖拽离开事件"""
    pass

def on_drag_over(event):
    """处理拖拽悬停事件"""
    if event.data.startswith('{'):
        event.accept()
    else:
        event.ignore()

def on_drop(event):
    """处理放置事件，获取拖拽的文件路径"""
    # 解析拖拽的文件路径
    data = event.data
    # 处理Windows系统的文件路径格式
    if data.startswith('{') and data.endswith('}'):
        data = data[1:-1]
    
    # 分割多个文件路径
    file_paths = data.split('} {')
    
    # 过滤非图片文件
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    valid_files = []
    for path in file_paths:
        if path.lower().endswith(image_extensions):
            valid_files.append(path)
    
    if valid_files:
        add_files_to_list(valid_files)
    else:
        messagebox.showwarning("警告", "请拖拽图片文件（支持jpg、jpeg、png、bmp、gif格式）")

def update_images():
    # 获取所有选中的文件
    selected_files = [file_list.get(i) for i in range(file_list.size())]
    if not selected_files:
        messagebox.showerror("错误", "请先选择图片文件")
        return

    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
    except ValueError:
        messagebox.showerror("错误", "请在宽度和高度中输入有效的数字")
        return

    # 统一设置为96dpi
    target_dpi = (96, 96)
    
    success_count = 0
    error_files = []

    for file_path in selected_files:
        try:
            with Image.open(file_path) as img:
                # 调整尺寸
                img = img.resize((width, height))
                # 保留原始EXIF数据
                exif_dict = img.info.get('exif', b'')
                # 使用目标DPI（96）保存文件
                img.save(file_path, exif=exif_dict, dpi=target_dpi)
            success_count += 1
        except Exception as e:
            error_files.append(f"{file_path}: {str(e)}")

    # 显示处理结果
    result_msg = f"成功处理 {success_count} 个文件，均已设置为96dpi\n"
    if error_files:
        result_msg += f"处理失败 {len(error_files)} 个文件:\n" + "\n".join(error_files)
    
    messagebox.showinfo("处理结果", result_msg)

# 创建主窗口
root = tk.Tk()
root.title("批量修改图片尺寸（统一96dpi）")
root.geometry("600x400")

# 启用窗口接受拖拽
root.drop_target_register('DND_Files')
root.dnd_bind('<<DropEnter>>', on_drag_enter)
root.dnd_bind('<<DropLeave>>', on_drag_leave)
root.dnd_bind('<<DropOver>>', on_drag_over)
root.dnd_bind('<<Drop>>', on_drop)

# 标签和输入框 - 默认宽度800
tk.Label(root, text="宽度:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
width_entry = tk.Entry(root)
width_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")
width_entry.insert(0, "800")  # 默认宽度800

# 标签和输入框 - 默认高度600
tk.Label(root, text="高度:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
height_entry = tk.Entry(root)
height_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
height_entry.insert(0, "600")  # 默认高度600

# 文件选择区域
tk.Label(root, text="选中的文件:").grid(row=3, column=0, padx=10, pady=5, sticky="ne")

# 创建带滚动条的列表框
file_frame = tk.Frame(root)
file_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")

scrollbar = Scrollbar(file_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

file_list = Listbox(file_frame, yscrollcommand=scrollbar.set, width=50, height=10)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=file_list.yview)

# 浏览按钮
file_button = tk.Button(root, text="浏览", command=select_files)
file_button.grid(row=3, column=2, padx=10, pady=5)

# 更新按钮
update_button = tk.Button(root, text="批量更新图片", command=update_images)
update_button.grid(row=4, column=0, columnspan=3, pady=10)

# 设置网格权重
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

# 运行主循环
root.mainloop()
    
