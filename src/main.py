import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import os

class DropTarget(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.files = []
        
        # 设置拖拽目标样式
        self.config(bg="#f0f0f0", relief=tk.SUNKEN, bd=2)
        self.grid_propagate(False)
        
        # 允许拖放设置
        self.configure(takefocus=True)
        self.bind("<Enter>", lambda e: self.focus_set())
        self.parent.bind("<ButtonPress-1>", lambda e: self.focus_set())
        
        # 添加提示文本
        self.label = tk.Label(self, text="拖放图片到此处\n或点击下方浏览按钮", 
                             bg="#f0f0f0", justify=tk.CENTER)
        self.label.pack(pady=10)
        
        # 添加文件列表显示区域
        self.file_list = scrolledtext.ScrolledText(self, height=6, width=40)
        self.file_list.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # 绑定拖拽事件（跨平台兼容格式）
        self.bind("<<DragEnter>>", self.on_drag_enter)
        self.bind("<<DragLeave>>", self.on_drag_leave)
        self.bind("<<Drop>>", self.on_drop)
        self.bind("<<Motion>>", self.on_motion)
        
        self.file_list.config(state=tk.DISABLED)

    def on_drag_enter(self, event):
        try:
            # 检查是否有拖入数据
            event.data
            self.config(bg="#e0f0e0")
            return event.action
        except:
            return

    def on_drag_leave(self, event):
        self.config(bg="#f0f0f0")

    def on_motion(self, event):
        return event.action

    def on_drop(self, event):
        self.config(bg="#f0f0f0")
        # 解析拖入的文件路径
        data = event.data.strip('{}')
        files = [f.strip() for f in data.split('} {')]
        
        # 过滤非图片文件
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
        valid_files = [f for f in files if f.lower().endswith(image_extensions)]
        
        if valid_files:
            self.files = valid_files
            self.update_file_list()
        return event.action

    def update_file_list(self):
        self.file_list.config(state=tk.NORMAL)
        self.file_list.delete(1.0, tk.END)
        for file in self.files:
            self.file_list.insert(tk.END, f"{os.path.basename(file)}\n")
        self.file_list.config(state=tk.DISABLED)

    def get_files(self):
        return self.files

    def set_files(self, files):
        self.files = files
        self.update_file_list()

def select_files(drop_target):
    file_paths = filedialog.askopenfilenames(
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
    )
    if file_paths:
        drop_target.set_files(list(file_paths))

def update_exif(drop_target):
    files = drop_target.get_files()
    if not files:
        messagebox.showerror("错误", "请先选择图片文件")
        return

    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
        dpi = int(dpi_entry.get())
        if width <= 0 or height <= 0 or dpi <= 0:
            raise ValueError("数值必须为正数")
    except ValueError as e:
        messagebox.showerror("错误", f"请输入有效的数字: {str(e)}")
        return

    success_count = 0
    error_files = []

    for file_path in files:
        try:
            with Image.open(file_path) as img:
                # 调整尺寸
                img = img.resize((width, height))
                # 保留原有EXIF数据
                exif_dict = img.info.get('exif', b'')
                # 保存文件
                img.save(file_path, exif=exif_dict, dpi=(dpi, dpi))
            success_count += 1
        except Exception as e:
            error_files.append(f"{os.path.basename(file_path)}: {str(e)}")

    # 显示处理结果
    result_msg = f"成功处理 {success_count} 个文件\n"
    if error_files:
        result_msg += f"处理失败 {len(error_files)} 个文件:\n" + "\n".join(error_files)
    
    messagebox.showinfo("处理结果", result_msg)

# 创建主窗口
root = tk.Tk()
root.title("批量修改图片尺寸")
root.geometry("600x400")

# 标签和输入框
tk.Label(root, text="宽度:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
width_entry = tk.Entry(root)
width_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
width_entry.insert(0, "588")

tk.Label(root, text="高度:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
height_entry = tk.Entry(root)
height_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
height_entry.insert(0, "354")

tk.Label(root, text="DPI:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
dpi_entry = tk.Entry(root)
dpi_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
dpi_entry.insert(0, "300")

# 文件拖放区域
tk.Label(root, text="图片文件:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.NE)
drop_target = DropTarget(root)
drop_target.grid(row=3, column=1, padx=10, pady=5, sticky=tk.NSEW)

# 浏览按钮
browse_button = tk.Button(root, text="浏览", command=lambda: select_files(drop_target))
browse_button.grid(row=3, column=2, padx=10, pady=5)

# 更新EXIF数据按钮
update_button = tk.Button(root, text="批量更新图片", command=lambda: update_exif(drop_target))
update_button.grid(row=4, column=0, columnspan=3, pady=10)

# 设置网格权重，使拖放区域可伸缩
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(1, weight=1)

# 运行主循环
root.mainloop()
