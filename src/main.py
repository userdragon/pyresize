import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import os
import sys

class DropTarget(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.files = []
        
        # 设置拖拽目标样式
        self.config(bg="#f0f0f0", relief=tk.SUNKEN, bd=2)
        self.grid_propagate(False)
        
        # 添加提示文本
        self.label = tk.Label(self, text="拖放图片到此处\n或点击下方浏览按钮", 
                             bg="#f0f0f0", justify=tk.CENTER)
        self.label.pack(pady=10)
        
        # 添加文件列表显示区域
        self.file_list = scrolledtext.ScrolledText(self, height=6, width=40)
        self.file_list.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # 配置拖放支持
        self._configure_drag_and_drop()
        
        # 调试用状态标签
        self.status_label = tk.Label(self, text="就绪", bg="#f0f0f0", font=("Arial", 8))
        self.status_label.pack(pady=5)
        
        self.file_list.config(state=tk.DISABLED)

    def _configure_drag_and_drop(self):
        # 基础事件绑定 - 用于跟踪拖放状态
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_click)
        
        # 跨平台拖放配置
        if sys.platform.startswith('win'):
            self._setup_windows_drag_drop()
        else:
            # 类Unix平台 (Linux/macOS)
            self.bind("<<DragEnter>>", self._on_drag_enter)
            self.bind("<<DragLeave>>", self._on_drag_leave)
            self.bind("<<Drop>>", self.on_drop)
            self.bind("<B1-Motion>", self._on_drag_motion)
        
        # 允许接受数据
        self.focus_set()
        self.configure(takefocus=True)

    def _setup_windows_drag_drop(self):
        # Windows平台拖放设置
        try:
            import ctypes
            from ctypes import wintypes
            
            # 注册窗口接受文件拖放
            hwnd = self.winfo_id()
            ctypes.windll.shell32.DragAcceptFiles(hwnd, True)
            
            # 定义窗口过程回调函数
            def wndproc(hwnd, msg, wparam, lparam):
                if msg == 0x0233:  # WM_DROPFILES
                    self.status_label.config(text="检测到拖放文件")
                    self._process_win32_drop_files(wparam)
                    return 0
                return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
            
            # 设置窗口过程
            self.original_wndproc = ctypes.windll.user32.SetWindowLongW(
                hwnd, 
                -4,  # GWL_WNDPROC
                ctypes.CFUNCTYPE(wintypes.LONG, wintypes.HWND, wintypes.UINT, 
                               wintypes.WPARAM, wintypes.LPARAM)(wndproc)
            )
            
            self.status_label.config(text="Windows拖放已启用")
        except Exception as e:
            self.status_label.config(text=f"拖放初始化: {str(e)[:30]}")
            # 备选方案 - 使用通用拖放处理
            self.bind("<<Drop>>", self._windows_drop_fallback)

    def _process_win32_drop_files(self, hdrop):
        # 处理Windows平台的拖放文件
        try:
            import ctypes
            from ctypes import wintypes
            
            num_files = ctypes.windll.shell32.DragQueryFileW(hdrop, -1, None, 0)
            self.status_label.config(text=f"发现 {num_files} 个文件")
            
            files = []
            for i in range(num_files):
                # 获取文件名长度
                buf_size = ctypes.windll.shell32.DragQueryFileW(hdrop, i, None, 0) + 1
                buffer = ctypes.create_unicode_buffer(buf_size)
                
                # 获取文件名
                ctypes.windll.shell32.DragQueryFileW(hdrop, i, buffer, buf_size)
                files.append(buffer.value)
            
            # 释放拖放数据
            ctypes.windll.shell32.DragFinish(hdrop)
            
            # 处理文件
            self._process_dropped_files(files)
        except Exception as e:
            self.status_label.config(text=f"处理错误: {str(e)[:30]}")

    def _windows_drop_fallback(self, event):
        # Windows平台拖放备选处理方案
        try:
            self.status_label.config(text="尝试处理拖放文件")
            if hasattr(event, 'data') and event.data:
                data = event.data.strip('{}')
                files = [f.strip() for f in data.split('} {') if f.strip()]
                self._process_dropped_files(files)
            else:
                self.status_label.config(text="未检测到文件数据")
        except Exception as e:
            self.status_label.config(text=f"备选处理错误: {str(e)[:30]}")

    def _on_drag_enter(self, event):
        self.config(bg="#e0f0e0")
        self.status_label.config(text="拖入文件中...")
        return "break"

    def _on_drag_leave(self, event):
        self.config(bg="#f0f0f0")
        self.status_label.config(text="文件已拖出")

    def _on_enter(self, event):
        self.focus_set()
        return "break"

    def _on_leave(self, event):
        if not self.winfo_containing(event.x_root, event.y_root) == self:
            self.config(bg="#f0f0f0")

    def _on_click(self, event):
        self.focus_set()

    def _on_drag_motion(self, event):
        return "break"

    def on_drop(self, event):
        self.config(bg="#f0f0f0")
        
        # 处理类Unix平台的拖放
        try:
            self.status_label.config(text="处理拖放文件")
            if hasattr(event, 'data') and event.data:
                data = event.data.strip('{}')
                files = [f.strip() for f in data.split('} {') if f.strip()]
                self._process_dropped_files(files)
            else:
                self.status_label.config(text="未检测到文件数据")
        except Exception as e:
            self.status_label.config(text=f"拖放错误: {str(e)[:30]}")
        
        return "break"

    def _process_dropped_files(self, files):
        # 过滤非图片文件
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
        valid_files = []
        
        for file in files:
            # 检查文件是否存在且是图片
            if os.path.isfile(file):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    valid_files.append(file)
        
        # 更新状态和文件列表
        if valid_files:
            self.files = valid_files
            self.update_file_list()
            self.status_label.config(text=f"已加载 {len(valid_files)} 个图片文件")
        else:
            self.status_label.config(text="未找到有效的图片文件")

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
        self.status_label.config(text=f"已选择 {len(files)} 个文件")

def select_files(drop_target):
    file_paths = filedialog.askopenfilenames(
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp")]
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
root.geometry("600x450")  # 增加高度以容纳状态标签

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
    
