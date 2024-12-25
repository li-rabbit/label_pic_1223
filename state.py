import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class ImageTagger:
    def __init__(self, root):
        self.photo = None
        self.image_label = None
        self.root = root
        self.root.title("图像标注工具")

        # 初始化变量
        self.image_list = []
        self.current_index = 0
        self.current_image_path = ""
        self.tags = ["云", "薄雾", "雨", "夜晚", "小型船只", "烟雾"]
        self.selected_tags = set()  # 使用集合存储选中的标签
        self.tag_buttons = {}  # 存储标签按钮引用

        # 创建界面
        self.create_widgets()

        # 选择文件夹并加载图像
        self.select_folder()
        self.load_images()
        if self.image_list:
            self.display_image()
        else:
            self.update_status("选择的文件夹中没有图像文件。")
            self.root.quit()

    def create_widgets(self):
        # 图像显示区域
        self.image_label = tk.Label(self.root)
        self.image_label.pack(padx=10, pady=10)

        # 标签选择区域
        tags_frame = tk.Frame(self.root)
        tags_frame.pack(padx=10, pady=5)

        for tag in self.tags:
            btn = tk.Button(tags_frame, text=tag, width=12, relief="raised",
                            command=lambda t=tag: self.toggle_tag(t))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.tag_buttons[tag] = btn  # 存储按钮引用

        # 按钮区域
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(padx=10, pady=10)

        self.bulk_tag_button = tk.Button(buttons_frame, text="全部标记", command=self.bulk_tag_images, width=12)
        self.bulk_tag_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = tk.Button(buttons_frame, text="上一张", command=self.prev_image, width=10)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(buttons_frame, text="下一张", command=self.next_image, width=10)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # 状态标签区域
        self.status_label = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 10))

    def select_folder(self):
        # 选择源文件夹
        self.source_folder = filedialog.askdirectory(title="选择源文件夹")
        if not self.source_folder:
            self.update_status("未选择任何文件夹。程序将退出。")
            self.root.quit()

    def load_images(self):
        # 加载文件夹中的图像文件
        supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
        self.image_list = [f for f in os.listdir(self.source_folder) if f.lower().endswith(supported_extensions)]
        self.image_list.sort()

    def display_image(self):
        # 显示当前图像
        image_path = os.path.join(self.source_folder, self.image_list[self.current_index])
        self.current_image_path = image_path
        try:
            img = Image.open(image_path)
            img = img.resize((800, 600), Image.LANCZOS)  # 使用 Image.LANCZOS
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.photo)
            self.root.title(f"图像标注工具 - {self.image_list[self.current_index]}")
        except Exception as e:
            self.update_status(f"无法打开图像文件：{e}")
            return

        # 重置所有标签按钮
        self.reset_tags()

    def reset_tags(self):
        """将所有标签按钮重置为未选中状态。"""
        self.selected_tags.clear()
        for btn in self.tag_buttons.values():
            btn.config(relief="raised", bg=self.root.cget('bg'))  # 恢复默认外观

    def toggle_tag(self, tag):
        """切换标签的选中状态，并更新按钮外观。"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            self.tag_buttons[tag].config(relief="raised", bg=self.root.cget('bg'))  # 未选中状态
            self.update_status(f"标签 '{tag}' 取消选择。")
        else:
            self.selected_tags.add(tag)
            self.tag_buttons[tag].config(relief="sunken", bg="lightblue")  # 选中状态
            self.update_status(f"标签 '{tag}' 选中。")

    def tag_image(self):
        """应用所选标签到当前图像，并重命名文件。"""
        # 获取选中的标签
        selected_tags = list(self.selected_tags)
        if not selected_tags:
            self.update_status("未选择任何标签。")
            return False  # 标记未成功

        # 构建新的文件名
        original_name, ext = os.path.splitext(self.image_list[self.current_index])

        # 检查是否已经包含某些标签，避免重复添加
        existing_tags = original_name.split("_")[1:]  # 假设原名格式为 "name_tag1_tag2"
        new_tags = [tag for tag in selected_tags if tag not in existing_tags]

        if not new_tags:
            self.update_status("所选标签已存在于文件名中。")
            return False  # 标记未成功

        all_tags = existing_tags + new_tags
        new_tags_str = "_".join(all_tags)
        new_name = f"{original_name.split('_')[0]}_{new_tags_str}{ext}"

        original_path = os.path.join(self.source_folder, self.image_list[self.current_index])
        new_path = os.path.join(self.source_folder, new_name)

        try:
            os.rename(original_path, new_path)
            self.update_status(f"文件已重命名为：{new_name}")
            # 更新图像列表
            self.image_list[self.current_index] = new_name
            # 清除所有选中的标签
            self.reset_tags()
            return True  # 标记成功
        except Exception as e:
            self.update_status(f"重命名文件失败：{e}")
            return False  # 标记未成功

    def bulk_tag_images(self):
        """将所选标签应用到所有图像。"""
        # 获取选中的标签
        selected_tags = list(self.selected_tags)
        if not selected_tags:
            self.update_status("未选择任何标签。")
            return

        # 遍历所有图像并添加标签
        renamed_count = 0
        for idx, filename in enumerate(self.image_list):
            original_path = os.path.join(self.source_folder, filename)
            original_name, ext = os.path.splitext(filename)

            # 检查是否已经包含某些标签，避免重复添加
            existing_tags = original_name.split("_")[1:]  # 假设原名格式为 "name_tag1_tag2"
            new_tags = [tag for tag in selected_tags if tag not in existing_tags]

            if not new_tags:
                continue  # 跳过已包含所有选中标签的图像

            all_tags = existing_tags + new_tags
            new_tags_str = "_".join(all_tags)
            new_name = f"{original_name.split('_')[0]}_{new_tags_str}{ext}"
            new_path = os.path.join(self.source_folder, new_name)

            try:
                os.rename(original_path, new_path)
                self.image_list[idx] = new_name
                renamed_count += 1
            except Exception as e:
                self.update_status(f"重命名文件 {filename} 失败：{e}")

        self.update_status(f"已成功标记 {renamed_count} 张图像。")
        # 重置标签选择
        self.reset_tags()
        # 显示当前索引的图像（可能已被重命名）
        self.display_image()

    def next_image(self):
        """在标记当前图像后，加载下一张图像。"""
        # 先标记当前图像
        success = self.tag_image()
        if not success:
            # 如果标记失败，提示并允许用户继续（根据需求调整）
            pass  # 这里选择不阻止用户继续
        # 切换到下一张图像
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image()
        else:
            self.update_status("已经是最后一张图像。")

    def prev_image(self):
        """切换到上一张图像。"""
        # 这里不强制标记当前图像，用户可以选择手动标记
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image()
        else:
            self.update_status("已经是第一张图像。")

    def update_status(self, message):
        """更新状态标签的文本。"""
        self.status_label.config(text=message)
        self.status_label.update_idletasks()  # 确保文本立即更新


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageTagger(root)
    root.mainloop()
