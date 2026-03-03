import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import customtkinter as ctk
from pathlib import Path
from core.batch_processor import AsyncBatchProcessor
from utils.config_manager import ConfigManager
from utils.dependency_manager import ensure_dependencies


class Word2PPTApp(ctk.CTk):
    """
    Word2PPT Assistant 主界面
    """

    def __init__(self):
        super().__init__()

        # 配置窗口
        self.title("Word2PPT Assistant - Word文档转PPT工具")
        self.geometry("850x600")  # 黄金比例

        # 配置Grid布局
        self.grid_columnconfigure(1, weight=1)  # 右侧工作区自适应变宽
        self.grid_rowconfigure(0, weight=1)     # 垂直方向自适应

        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 初始化批量处理器（稍后在开始转换时指定模型）
        self.processor = None

        # 日志队列，用于线程安全更新
        self.log_queue = queue.Queue()

        # 首先检查并安装依赖
        print("正在检查依赖...")  # 使用 print 而不是 log_message，因为在 setup_ui 之前
        try:
            ensure_dependencies()
        except Exception as e:
            print(f"依赖检查失败: {str(e)}")
            # 即使依赖安装失败也要继续，让用户手动解决

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 创建左侧控制栏
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)  # 防止frame自动调整大小

        # 配置sidebar的grid权重，让底部按钮沉底
        sidebar.grid_rowconfigure(0, weight=0)  # 标题
        sidebar.grid_rowconfigure(1, weight=0)  # 文件操作区
        sidebar.grid_rowconfigure(2, weight=0)  # 设置区
        sidebar.grid_rowconfigure(3, weight=0)  # 模型选择
        sidebar.grid_rowconfigure(4, weight=0)  # API状态
        sidebar.grid_rowconfigure(5, weight=1)  # 空白区域，占用剩余空间
        sidebar.grid_rowconfigure(6, weight=0)  # 底部按钮区域

        # 应用标题
        title_label = ctk.CTkLabel(
            sidebar,
            text="Word2PPT 转换器",
            font=("微软雅黑", 20, "bold")
        )
        title_label.grid(row=0, column=0, pady=(30, 20))

        # 文件操作区
        file_operations_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        file_operations_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        file_operations_frame.grid_columnconfigure(0, weight=1)

        # 选择单个 Word 文件按钮
        single_file_btn = ctk.CTkButton(
            file_operations_frame,
            text="选择单个 Word 文件",
            height=36,
            corner_radius=6,
            command=self.select_single_file
        )
        single_file_btn.grid(row=0, column=0, padx=0, pady=5, sticky="ew")

        # 选择包含 Word 的文件夹按钮
        folder_btn = ctk.CTkButton(
            file_operations_frame,
            text="选择包含 Word 的文件夹",
            height=36,
            corner_radius=6,
            command=self.select_folder
        )
        folder_btn.grid(row=1, column=0, padx=0, pady=5, sticky="ew")

        # 设置区
        settings_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        settings_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 10))
        settings_frame.grid_columnconfigure(0, weight=1)

        # 开发者模式复选框
        self.dev_mode_var = tk.BooleanVar(value=False)  # 默认不开启开发者模式
        self.dev_mode_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="开发者模式",
            variable=self.dev_mode_var,
            font=("微软雅黑", 12)
        )
        self.dev_mode_checkbox.grid(row=0, column=0, sticky="w", padx=0, pady=0)

        # 模型选择下拉框
        model_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        model_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 10))
        model_frame.grid_columnconfigure(0, weight=1)

        model_label = ctk.CTkLabel(model_frame, text="模型选择:", font=("微软雅黑", 12))
        model_label.grid(row=0, column=0, sticky="w", padx=0, pady=(0, 5))

        # 获取可用模型列表
        available_models = list(self.config_manager.config.get('models', {}).keys())
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            values=available_models if available_models else ["deepseek", "qwen"],
            state="readonly",
            height=30
        )
        default_model = self.config_manager.get_default_model()
        self.model_combo.set(default_model)  # 设置默认值
        self.model_combo.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # 绑定模型选择变化事件
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_change)

        # API Key 状态标签
        self.api_status_label = ctk.CTkLabel(
            sidebar,
            text="API Key: 未配置",
            text_color="red",
            font=("微软雅黑", 10)
        )
        self.api_status_label.grid(row=4, column=0, sticky="w", padx=30, pady=(5, 10))

        # 底部按钮区域
        bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=20)
        bottom_frame.grid_columnconfigure(0, weight=1)

        # 开始转换按钮 - 放在底部frame的最后一行
        self.start_btn = ctk.CTkButton(
            bottom_frame,
            text="开始批量转换",
            command=self.start_conversion,
            fg_color="#1f6aa5",
            hover_color="#144870",
            height=45,
            font=("微软雅黑", 15, "bold")
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))

        # 停止按钮
        self.stop_btn = ctk.CTkButton(
            bottom_frame,
            text="强制停止",
            command=self.stop_conversion,
            fg_color="red",
            hover_color="darkred",
            height=40,
            font=("微软雅黑", 13, "bold"),
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=1, column=0, sticky="ew", padx=0, pady=5)

        # 创建右侧主工作区
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        workspace.grid_rowconfigure(1, weight=1)  # 日志面板行自适应
        workspace.grid_columnconfigure(0, weight=1)  # 日志面板列自适应

        # 状态栏/标题
        status_label = ctk.CTkLabel(
            workspace,
            text="处理日志 / 运行状态",
            font=("微软雅黑", 14, "bold")
        )
        status_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # 大日志面板
        self.log_text = ctk.CTkTextbox(
            workspace,
            corner_radius=10,
            font=("微软雅黑", 13),
            activate_scrollbars=True
        )
        self.log_text.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # 检查 API Key 是否存在
        self.check_api_key()

        # 配置日志队列
        self.log_queue = queue.Queue()

    def select_single_file(self):
        """选择单个Word文件"""
        # 获取上次使用的输入文件夹路径
        last_input_path = self.config_manager.get_last_used_path("input_folder")

        file_path = filedialog.askopenfilename(
            title="选择Word文档",
            initialdir=last_input_path if last_input_path else ".",
            filetypes=[("Word文档", "*.docx")]
        )
        if file_path:
            self.log_message(f"已选择文件: {Path(file_path).name}")
            self.log_message(f"完整路径: {file_path}")
            # 记住输入文件夹路径
            input_folder = str(Path(file_path).parent)
            self.config_manager.set_last_used_path("input_folder", input_folder)

    def select_folder(self):
        """选择包含Word文档的文件夹"""
        # 获取上次使用的输入文件夹路径
        last_input_path = self.config_manager.get_last_used_path("input_folder")

        folder_path = filedialog.askdirectory(
            title="选择包含Word文档的文件夹",
            initialdir=last_input_path if last_input_path else "."
        )
        if folder_path:
            self.log_message(f"已选择文件夹: {Path(folder_path).name}")
            self.log_message(f"完整路径: {folder_path}")
            # 记住输入文件夹路径
            self.config_manager.set_last_used_path("input_folder", folder_path)

    def on_model_change(self, event=None):
        """处理模型选择变化"""
        self.check_api_key()

    def check_api_key(self):
        """检查 API Key 是否存在"""
        selected_model = self.model_combo.get()
        api_key = self.config_manager.get_api_key(selected_model)

        if api_key and api_key.strip():
            self.api_status_label.configure(text=f"API Key: {selected_model} 已配置", text_color="green")
        else:
            self.api_status_label.configure(text=f"API Key: {selected_model} 未配置", text_color="red")

    def start_conversion(self):
        """开始批量转换"""
        # 检查 API Key
        selected_model = self.model_combo.get()
        api_key = self.config_manager.get_api_key(selected_model)

        if not api_key or not api_key.strip():
            self.log_message(f"错误: {selected_model} 的 API Key 未配置，请在 config.json 中设置!")
            return

        # 更新按钮状态
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)

        # 清空日志
        self.log_text.delete("0.0", tk.END)
        self.log_message("开始批量转换...")

        # 创建新的处理器实例，传递开发者模式状态
        is_dev_mode = self.dev_mode_var.get()
        self.processor = AsyncBatchProcessor(
            log_callback=self.log_message,
            model_name=selected_model,
            keep_temp_files=is_dev_mode,
            dev_mode=is_dev_mode
        )

        # 获取上次使用的输入文件夹路径，如果没有则使用默认路径
        last_input_path = self.config_manager.get_last_used_path("input_folder")
        input_dir = last_input_path if last_input_path else None

        # 在后台线程启动处理
        self.processor.start_processing(input_dir=input_dir)

        # 启动日志更新循环
        self.after(100, self.update_logs)

    def stop_conversion(self):
        """停止转换"""
        if self.processor:
            self.processor.stop_processing()
        self.log_message("正在停止处理...")

        # 等待处理结束
        while self.processor and self.processor.is_running:
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
        if self.processor and self.processor.is_running:
            self.after(100, self.update_logs)
        else:
            self.reset_buttons()


def main():
    """主函数"""
    app = Word2PPTApp()
    app.mainloop()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception as e:
        # 获取完整错误信息
        error_msg = traceback.format_exc()

        # 获取应用程序路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            base_path = Path(sys.executable).parent
        else:
            # 开发环境
            base_path = Path(__file__).parent

        # 写入崩溃日志
        crash_log_path = base_path / "crash_log.txt"
        with open(crash_log_path, "w", encoding="utf-8") as f:
            f.write(f"Word2PPT-Assistant 崩溃日志\n")
            f.write(f"时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"错误类型: {type(e).__name__}\n")
            f.write(f"错误信息: {str(e)}\n")
            f.write("\n")
            f.write("=" * 60 + "\n")
            f.write("完整堆栈跟踪:\n")
            f.write("=" * 60 + "\n")
            f.write(error_msg)

        # 同时在控制台输出
        print(f"程序发生严重错误，已记录到 crash_log.txt")
        print(error_msg)

        # 退出前显示错误信息
        if getattr(sys, 'frozen', False):
            # 打包后弹出对话框显示错误
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("严重错误", f"程序发生严重错误，已记录到 crash_log.txt\n\n{str(e)}")
            root.destroy()

        import sys
        sys.exit(1)