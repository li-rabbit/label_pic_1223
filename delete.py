import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class ImageMoverApp:
    def __init__(self, master):
        self.photo = None
        self.status_label = None
        self.image_label = None
        self.btn_target = None
        self.btn_source = None
        self.master = master
        self.master.title("图像移动工具")
        self.master.geometry("800x600")

        # 设置源文件夹和目标文件夹
        self.source_folder = ""
        self.target_folder = ""

        # 图像列表和当前索引
        self.image_list = []
        self.current_index = 0

        # 设置UI
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=10, pady=10)

        # 按钮选择源文件夹
        self.btn_source = tk.Button(frame, text="选择源文件夹", command=self.select_source_folder)
        self.btn_source.grid(row=0, column=0, padx=5, pady=5)

        # 按钮选择目标文件夹
        self.btn_target = tk.Button(frame, text="选择目标文件夹", command=self.select_target_folder)
        self.btn_target.grid(row=0, column=1, padx=5, pady=5)

        # 标签显示当前图像
        self.image_label = tk.Label(self.master)
        self.image_label.pack(padx=10, pady=10, expand=True)

        # 状态标签
        self.status_label = tk.Label(self.master, text="请先选择源和目标文件夹")
        self.status_label.pack(padx=10, pady=5)

        # 绑定键盘事件
        self.master.bind("<Left>", self.show_prev_image)
        self.master.bind("<Right>", self.show_next_image)
        self.master.bind("<Down>", self.move_image)

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="选择源文件夹")
        if folder:
            self.source_folder = folder
            self.load_images()
            self.status_label.config(text=f"源文件夹: {self.source_folder}")
            self.show_image()

    def select_target_folder(self):
        folder = filedialog.askdirectory(title="选择目标文件夹")
        if folder:
            self.target_folder = folder
            self.status_label.config(text=f"目标文件夹: {self.target_folder}")

    def load_images(self):
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        self.image_list = [f for f in os.listdir(self.source_folder) if f.lower().endswith(supported_formats)]
        self.image_list.sort()
        self.current_index = 0

    def show_image(self):
        if not self.image_list:
            self.image_label.config(image='')
            self.status_label.config(text="没有找到图像文件")
            return

        image_path = os.path.join(self.source_folder, self.image_list[self.current_index])
        try:
            img = Image.open(image_path)
            img.thumbnail((800, 600))  # 调整图像大小
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo)
            self.status_label.config(
                text=f"显示 {self.current_index + 1} / {len(self.image_list)}: {self.image_list[self.current_index]}")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图像: {e}")

    def show_prev_image(self, event=None):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()
        else:
            messagebox.showinfo("提示", "已经是第一张图像")

    def show_next_image(self, event=None):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.show_image()
        else:
            messagebox.showinfo("提示", "已经是最后一张图像")

    def move_image(self, event=None):
        if not self.target_folder:
            messagebox.showwarning("警告", "请先选择目标文件夹")
            return

        if not self.image_list:
            messagebox.showwarning("警告", "没有图像可以移动")
            return

        image_name = self.image_list[self.current_index]
        src_path = os.path.join(self.source_folder, image_name)
        dst_path = os.path.join(self.target_folder, image_name)

        try:
            shutil.move(src_path, dst_path)
            self.status_label.config(text=f"已移动: {image_name} 到 {self.target_folder}")
            # 移除已移动的图像并显示下一张
            del self.image_list[self.current_index]
            if self.current_index >= len(self.image_list):
                self.current_index = len(self.image_list) - 1
            self.show_image()
        except Exception as e:
            messagebox.showerror("错误", f"无法移动图像: {e}")


def main():
    root = tk.Tk()
    app = ImageMoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
