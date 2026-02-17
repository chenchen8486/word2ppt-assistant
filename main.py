import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.doc_loader import DocLoader
from core.standardizer import Standardizer
from core.llm_client import LLMClient
from core.ppt_generator import PPTGenerator
from utils.logger import setup_logger
from utils.config_manager import ConfigManager

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Model Mapping
MODEL_MAPPING = {
    "DeepSeek-V3 (Chat)": "deepseek-chat",
    "DeepSeek-R1 (Reasoner)": "deepseek-reasoner"
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Exam2PPT - AI 试卷转 PPT 助手")
        self.geometry("800x650") # Increased height for better layout

        # Config Manager
        self.config = ConfigManager()

        # Variables
        self.api_key_var = ctk.StringVar(value=self.config.get("api_key", ""))
        self.base_url_var = ctk.StringVar(value=self.config.get("base_url", "https://api.deepseek.com"))
        self.model_var = ctk.StringVar(value=self.config.get("model", "DeepSeek-V3 (Chat)"))
        self.file_path_var = ctk.StringVar()
        self.output_dir_var = ctk.StringVar(value=self.config.get("last_output_dir", ""))
        self.status_var = ctk.StringVar(value="Ready")
        self.is_running = False
        self.stop_event = threading.Event()

        # Layout
        self._create_widgets()
        
        # Initialize Logger with GUI callback
        self.logger = setup_logger(gui_callback=self.append_log)

        # On Close Handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_widgets(self):
        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # 1. API Config Section
        api_frame = ctk.CTkFrame(self)
        api_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        # Row 0: API Key and Base URL
        ctk.CTkLabel(api_frame, text="API Key:").grid(row=0, column=0, padx=10, pady=10)
        self.api_entry = ctk.CTkEntry(api_frame, textvariable=self.api_key_var, show="*", width=250)
        self.api_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(api_frame, text="Base URL:").grid(row=0, column=2, padx=10, pady=10)
        self.url_entry = ctk.CTkEntry(api_frame, textvariable=self.base_url_var, width=200)
        self.url_entry.grid(row=0, column=3, padx=10, pady=10)

        # 2. Model Selection Section (Moved to separate row for visibility)
        model_frame = ctk.CTkFrame(self)
        model_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(model_frame, text="AI 模型:").pack(side="left", padx=10, pady=10)
        self.model_combo = ctk.CTkComboBox(model_frame, values=list(MODEL_MAPPING.keys()), variable=self.model_var, width=300)
        self.model_combo.pack(side="left", padx=10, pady=10)

        # 3. File Selection Section
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_select_file = ctk.CTkButton(file_frame, text="选择试卷 (.docx)", command=self.select_file)
        self.btn_select_file.grid(row=0, column=0, padx=10, pady=10)
        
        self.lbl_file_path = ctk.CTkLabel(file_frame, textvariable=self.file_path_var, text_color="gray")
        self.lbl_file_path.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.btn_select_out = ctk.CTkButton(file_frame, text="选择保存目录", command=self.select_output_dir)
        self.btn_select_out.grid(row=1, column=0, padx=10, pady=10)
        
        self.lbl_out_path = ctk.CTkLabel(file_frame, textvariable=self.output_dir_var, text_color="gray")
        self.lbl_out_path.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # 4. Control Section
        ctrl_frame = ctk.CTkFrame(self)
        ctrl_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_start = ctk.CTkButton(ctrl_frame, text="开始转换", command=self.start_task, fg_color="green")
        self.btn_start.pack(side="left", padx=20, pady=10)
        
        self.btn_stop = ctk.CTkButton(ctrl_frame, text="终止任务", command=self.stop_task, fg_color="red", state="disabled")
        self.btn_stop.pack(side="left", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(ctrl_frame)
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=20, pady=10)
        self.progress_bar.set(0)

        # 5. Log Section
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        
        ctk.CTkLabel(log_frame, text="运行日志").pack(anchor="w", padx=10, pady=5)
        self.log_textbox = ctk.CTkTextbox(log_frame)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)

    def select_file(self):
        initial_dir = self.config.get("last_file_dir", "/")
        path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("Word Document", "*.docx")])
        if path:
            self.file_path_var.set(path)
            # Save dir to config
            self.config.set("last_file_dir", os.path.dirname(path))
            
            # Default output dir to same folder if not set
            if not self.output_dir_var.get():
                out_dir = os.path.dirname(path)
                self.output_dir_var.set(out_dir)
                self.config.set("last_output_dir", out_dir)

    def select_output_dir(self):
        initial_dir = self.config.get("last_output_dir", "/")
        path = filedialog.askdirectory(initialdir=initial_dir)
        if path:
            self.output_dir_var.set(path)
            self.config.set("last_output_dir", path)

    def on_closing(self):
        """Save config on exit."""
        self.config.set("api_key", self.api_key_var.get())
        self.config.set("base_url", self.base_url_var.get())
        self.config.set("model", self.model_var.get())
        self.config.save_config()
        self.destroy()

    def append_log(self, message):
        """Thread-safe log appending."""
        def _update():
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
        self.after(0, _update)

    def toggle_controls(self, running):
        self.is_running = running
        state_start = "disabled" if running else "normal"
        state_stop = "normal" if running else "disabled"
        
        self.btn_start.configure(state=state_start)
        self.btn_select_file.configure(state=state_start)
        self.btn_select_out.configure(state=state_start)
        self.btn_stop.configure(state=state_stop)
        self.api_entry.configure(state=state_start) # Lock API input during run
        self.model_combo.configure(state=state_start)
        
        if running:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.set(0)

    def start_task(self):
        api_key = self.api_key_var.get()
        file_path = self.file_path_var.get()
        output_dir = self.output_dir_var.get()
        base_url = self.base_url_var.get()
        model_display = self.model_var.get()
        model = MODEL_MAPPING.get(model_display, "deepseek-chat")

        # Save config immediately
        self.config.set("api_key", api_key)
        self.config.set("base_url", base_url)
        self.config.set("model", model_display)
        self.config.save_config()

        if not api_key:
            self.append_log("[错误] 请输入 API Key。")
            return
        if not file_path or not os.path.exists(file_path):
            self.append_log("[错误] 请选择有效的 Word 文件。")
            return
        if not output_dir:
            self.append_log("[错误] 请选择保存目录。")
            return

        self.stop_event.clear()
        self.toggle_controls(True)
        
        # Start thread
        thread = threading.Thread(
            target=self.run_conversion,
            args=(api_key, base_url, model, file_path, output_dir),
            daemon=True
        )
        thread.start()

    def stop_task(self):
        if self.is_running:
            self.stop_event.set()
            self.append_log("[信息] 正在停止任务，请稍候...")
            # Note: The thread will check stop_event and exit gracefully.

    def run_conversion(self, api_key, base_url, model, file_path, output_dir):
        try:
            self.append_log(f"--- 任务开始: {os.path.basename(file_path)} ---")
            self.append_log(f"使用模型: {model}")
            
            # 1. Init Components
            # doc_loader = DocLoader(file_path) # Deprecated in favor of Standardizer
            llm_client = LLMClient(api_key, base_url, stop_event=self.stop_event)
            ppt_gen = PPTGenerator()
            
            # 2. Standardize & Parse (The new core logic)
            self.append_log("正在解析文档结构与提取内容...")
            standardizer = Standardizer(file_path, output_image_dir=os.path.join(output_dir, "temp_images"), llm_client=llm_client)
            
            if self.stop_event.is_set(): return
            
            # This runs the full pipeline: Load -> Filter -> Regex Parse -> LLM Refine
            # Since LLM Refine uses concurrency internally, we don't need external thread pool here for now.
            # But Standardizer.load_and_parse is synchronous blocking call (except internal threads).
            # We are already in a worker thread (run_conversion), so it's fine.
            
            # Hook logger? Standardizer uses get_logger() which writes to stdout/file.
            # To see logs in GUI, we rely on the fact that setup_logger configured a handler that might not be captured here?
            # Actually, main.py's setup_logger has gui_callback.
            # Standardizer's logger is obtained via get_logger().
            # We need to ensure Standardizer logs reach GUI.
            # get_logger() returns a singleton. If main.py initialized it with gui_callback, it should work.
            
            structured_data = standardizer.load_and_parse()
            
            if self.stop_event.is_set():
                self.append_log("[信息] 用户终止了任务。")
                return

            self.append_log(f"解析完成，共提取 {len([x for x in structured_data if x.get('type')=='question'])} 道题目。")

            # 3. Generate PPT
            if not structured_data:
                self.append_log("[警告] 未提取到任何有效内容，不生成 PPT。")
            else:
                self.append_log(f"正在生成 PPT...")
                filename = os.path.basename(file_path).rsplit('.', 1)[0]
                out_path = os.path.join(output_dir, f"{filename}_processed.pptx")
                
                ppt_gen.generate(structured_data, out_path, title=filename)
                self.append_log(f"完成！PPT 已保存至: {out_path}")
                
                # Completion Popup
                self.after(0, lambda: self.show_completion_dialog(out_path))

        except Exception as e:
            self.append_log(f"[错误] 发生意外错误: {str(e)}")
            import traceback
            self.append_log(traceback.format_exc())
        finally:
            self.after(0, lambda: self.toggle_controls(False))

    def show_completion_dialog(self, out_path):
        """Shows a completion message box."""
        msg = f"转换成功！\n文件已保存至:\n{out_path}"
        if messagebox.askyesno("任务完成", msg + "\n\n是否打开输出文件夹？"):
            try:
                folder = os.path.dirname(out_path)
                os.startfile(folder)
            except Exception as e:
                self.append_log(f"[错误] 无法打开文件夹: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
