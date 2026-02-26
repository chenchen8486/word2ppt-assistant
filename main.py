import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
from pathlib import Path
from core.batch_processor import AsyncBatchProcessor


class Word2PPTApp(ctk.CTk):
    """
    Word2PPT Assistant 主界面
    """

    def __init__(self):
        super().__init__()

        # 配置窗口
        self.title("Word2PPT Assistant - Word文档转PPT工具")
        self.geometry("1000x700")

        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 初始化批量处理器
        self.processor = AsyncBatchProcessor(log_callback=self.log_message)
        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 顶部区域：模型选择和API Key状态
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # 模型选择
        model_label = ctk.CTkLabel(top_frame, text="模型选择:")
        model_label.pack(side=tk.LEFT, padx=5)

        self.model_combo = ctk.CTkComboBox(
            top_frame,
            values=["DeepSeek", "Qwen", "GPT-4"],
            state="readonly"
        )
        self.model_combo.set("DeepSeek")  # 默认选择
        self.model_combo.pack(side=tk.LEFT, padx=5)

        # API Key 状态
        self.api_status_label = ctk.CTkLabel(top_frame, text="API Key: 未配置", text_color="red")
        self.api_status_label.pack(side=tk.RIGHT, padx=10)

        # 检查 API Key 是否存在
        self.check_api_key()

        # 中部区域：功能按钮
        middle_frame = ctk.CTkFrame(main_frame)
        middle_frame.pack(fill=tk.X, padx=10, pady=10)

        # 输入输出文件夹按钮
        input_btn = ctk.CTkButton(
            middle_frame,
            text="打开输入文件夹 (Input)",
            command=self.open_input_folder
        )
        input_btn.pack(side=tk.LEFT, padx=10, pady=10)

        output_btn = ctk.CTkButton(
            middle_frame,
            text="打开输出文件夹 (Output)",
            command=self.open_output_folder
        )
        output_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 底部区域：控制按钮
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        # 开始转换按钮
        self.start_btn = ctk.CTkButton(
            bottom_frame,
            text="开始批量转换",
            command=self.start_conversion,
            fg_color="green",
            hover_color="darkgreen",
            height=50
        )
        self.start_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 停止按钮
        self.stop_btn = ctk.CTkButton(
            bottom_frame,
            text="强制停止",
            command=self.stop_conversion,
            fg_color="red",
            hover_color="darkred",
            height=50,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10, pady=10)

        # 日志区域
        log_label = ctk.CTkLabel(main_frame, text="处理日志:")
        log_label.pack(anchor=tk.W, padx=10, pady=(10, 0))

        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 日志队列，用于线程安全更新
        self.log_queue = queue.Queue()

    def check_api_key(self):
        """检查 API Key 是否存在"""
        if os.path.exists("API_KEY.txt"):
            with open("API_KEY.txt", 'r', encoding='utf-8-sig') as f:
                key_content = f.read().strip()
                if key_content:
                    self.api_status_label.configure(text="API Key: 已配置", text_color="green")
                else:
                    self.api_status_label.configure(text="API Key: 未配置", text_color="red")
        else:
            self.api_status_label.configure(text="API Key: 未配置", text_color="red")

    def open_input_folder(self):
        """打开输入文件夹"""
        input_path = Path("data/01_input_docs").absolute()
        input_path.mkdir(parents=True, exist_ok=True)
        os.startfile(str(input_path))

    def open_output_folder(self):
        """打开输出文件夹"""
        output_path = Path("data/03_output_pptx").absolute()
        output_path.mkdir(parents=True, exist_ok=True)
        os.startfile(str(output_path))

    def start_conversion(self):
        """开始批量转换"""
        # 更新按钮状态
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)

        # 清空日志
        self.log_text.delete(1.0, tk.END)
        self.log_message("开始批量转换...")

        # 在后台线程启动处理
        self.processor.start_processing()

        # 启动日志更新循环
        self.after(100, self.update_logs)

    def stop_conversion(self):
        """停止转换"""
        self.processor.stop_processing()
        self.log_message("正在停止处理...")

        # 等待处理结束
        while self.processor.is_running:
            self.update()
            import time
            time.sleep(0.1)

        self.log_message("处理已停止")
        self.reset_buttons()

    def reset_buttons(self):
        """重置按钮状态"""
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)

    def log_message(self, message):
        """记录日志消息"""
        # 使用队列确保线程安全
        self.log_queue.put(f"[{self.get_timestamp()}] {message}\n")

    def get_timestamp(self):
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def update_logs(self):
        """更新日志显示"""
        # 处理队列中的所有消息
        while not self.log_queue.empty():
            try:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)  # 自动滚动到底部
            except queue.Empty:
                break

        # 如果处理器仍在运行，继续更新日志
        if self.processor.is_running:
            self.after(100, self.update_logs)
        else:
            self.reset_buttons()


def main():
    """主函数"""
    app = Word2PPTApp()
    app.mainloop()


if __name__ == "__main__":
    main()