import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)
        # 尝试读取并设置原图片的DPI
        try:
            with Image.open(file_path) as img:
                dpi = img.info.get('dpi', (300, 300))  # 默认300如果没有DPI信息
                dpi_entry.delete(0, tk.END)
                dpi_entry.insert(0, str(int(dpi[0])))  # 取水平DPI
        except Exception as e:
            messagebox.showwarning("警告", f"无法读取图片DPI信息，使用默认值: {e}")
            dpi_entry.delete(0, tk.END)
            dpi_entry.insert(0, "300")

def update_exif():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showerror("错误", "请先选择一个文件")
        return

    try:
        width = int(width_entry.get())
        height = int(height_entry.get())
        dpi = int(dpi_entry.get())
    except ValueError:
        messagebox.showerror("错误", "请在宽度、高度和DPI中输入有效的数字")
        return

    try:
        with Image.open(file_path) as img:
            img = img.resize((width, height))
            exif_dict = img.info.get('exif', b'')
            img.save(file_path, exif=exif_dict, dpi=(dpi, dpi))
        messagebox.showinfo("成功", "EXIF数据已更新")
    except Exception as e:
        messagebox.showerror("错误", f"无法修改EXIF数据: {e}")

# 创建主窗口
root = tk.Tk()
root.title("修改图片尺寸")

# 标签和输入框 - 宽度默认800
tk.Label(root, text="宽度:").grid(row=0, column=0, padx=10, pady=5)
width_entry = tk.Entry(root)
width_entry.grid(row=0, column=1, padx=10, pady=5)
width_entry.insert(0, "800")  # 修改默认宽度为800

# 标签和输入框 - 高度默认600
tk.Label(root, text="高度:").grid(row=1, column=0, padx=10, pady=5)
height_entry = tk.Entry(root)
height_entry.grid(row=1, column=1, padx=10, pady=5)
height_entry.insert(0, "600")  # 修改默认高度为600

# 标签和输入框 - DPI默认自动识别
tk.Label(root, text="DPI:").grid(row=2, column=0, padx=10, pady=5)
dpi_entry = tk.Entry(root)
dpi_entry.grid(row=2, column=1, padx=10, pady=5)
dpi_entry.insert(0, "96")  # 初始默认值，选择文件后会自动更新

# 文件选择框
tk.Label(root, text="选择文件:").grid(row=3, column=0, padx=10, pady=5)
file_entry = tk.Entry(root, width=40)
file_entry.grid(row=3, column=1, padx=10, pady=5)
file_button = tk.Button(root, text="浏览", command=select_file)
file_button.grid(row=3, column=2, padx=10, pady=5)

# 更新EXIF数据按钮
update_button = tk.Button(root, text="更新EXIF数据", command=update_exif)
update_button.grid(row=4, column=0, columnspan=3, pady=10)

# 运行主循环
root.mainloop()
