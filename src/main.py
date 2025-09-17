import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END, Button
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import os
import sys

def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发和打包后环境"""
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
    for path in file_paths:
        # 避免添加重复文件
        if path not in [file_list.get(i) for i in range(file_list.size())]:
            file_list.insert(END, path)

def on_drop(event):
    """处理放置事件，获取拖拽的文件路径"""
    data = event.data.strip()
    
    if '{' in data and '}' in data:
        data = data.replace('{', '').replace('}', '')
        file_paths = data.split()
    else:
        file_paths = data.split()
    
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    valid_files = []
    for path in file_paths:
        if os.path.exists(path) and path.lower().endswith(image_extensions):
            valid_files.append(path)
    
    if valid_files:
        add_files_to_list(valid_files)
    else:
        messagebox.showwarning("警告", "请拖拽有效的图片文件（支持jpg、jpeg、png、bmp、gif格式）")

def delete_selected():
    """删除选中的文件"""
    selected_indices = file_list.curselection()
    if not selected_indices:
        messagebox.showinfo("提示", "请先选中要删除的文件")
        return
    
    # 从后往前删除，避免索引变化导致错误
    for i in sorted(selected_indices, reverse=True):
        file_list.delete(i)

def delete_all():
    """删除所有文件"""
    if file_list.size() == 0:
        messagebox.showinfo("提示", "列表中没有文件可删除")
        return
    
    if messagebox.askyesno("确认", "确定要删除所有文件吗？"):
        file_list.delete(0, END)

def update_images():
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

    result_msg = f"成功处理 {success_count} 个文件，均已设置为96dpi\n"
    if error_files:
        result_msg += f"处理失败 {len(error_files)} 个文件:\n" + "\n".join(error_files)
    
    messagebox.showinfo("处理结果", result_msg)

def test_drag_and_drop():
    """测试拖拽功能是否真正可用"""
    try:
        # 尝试执行一个简单的拖拽相关操作来验证功能
        root.call('::tkdnd::version')
        return True
    except:
        return False

# 初始化主窗口
root = TkinterDnD.Tk()
root.title("批量修改图片尺寸（统一96dpi）")
root.geometry("700x450")

# 优化tkdnd库初始化检测
tkdnd_path = resource_path('tkdnd2.9.2')
try:
    # 尝试初始化tkdnd库
    root.eval(f'::tkdnd::initialise "{tkdnd_path}" "tkdnd292.dll" "tkdnd"')
    
    # 实际测试拖拽功能是否可用
    if not test_drag_and_drop():
        raise Exception("拖拽功能测试失败")
except:
    # 只有在确实无法使用时才显示提示
    messagebox.showwarning("提示", "拖拽功能可能无法使用，建议使用浏览按钮选择文件")

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
tk.Label(root, text="选中的文件:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")

file_frame = tk.Frame(root)
file_frame.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

scrollbar = Scrollbar(file_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

file_list = Listbox(file_frame, yscrollcommand=scrollbar.set, width=50, height=10, selectmode=tk.EXTENDED)
file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
file_list.drop_target_register(DND_FILES)
file_list.dnd_bind('<<Drop>>', on_drop)

scrollbar.config(command=file_list.yview)

# 按钮区域
button_frame = tk.Frame(root)
button_frame.grid(row=2, column=2, padx=10, pady=5, sticky="ns")

file_button = Button(button_frame, text="浏览", command=select_files, width=10)
file_button.pack(pady=5, fill=tk.X)

delete_selected_btn = Button(button_frame, text="删除选中", command=delete_selected, width=10)
delete_selected_btn.pack(pady=5, fill=tk.X)

delete_all_btn = Button(button_frame, text="删除全部", command=delete_all, width=10)
delete_all_btn.pack(pady=5, fill=tk.X)

# 更新按钮
update_button = Button(root, text="批量更新图片", command=update_images)
update_button.grid(row=3, column=0, columnspan=3, pady=10)

# 网格配置
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
    
