import os
import threading
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from core.doc_loader import DocLoader
from core.llm_client import LLMClient
from core.ppt_generator import PPTGenerator
from utils.marp_manager import MarpManager

# Set theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Word to PPT Converter (Markdown Native Workflow)")
        self.geometry("900x600")

        # Variables
        self.api_key_var = ctk.StringVar()
        self.model_var = ctk.StringVar(value="deepseek-chat")
        self.file_path_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Ready")
        self.is_processing = False
        self.stop_event = threading.Event()

        # Load API Key if exists
        self.load_api_key()

        # UI Layout
        self.create_widgets()

    def load_api_key(self):
        if os.path.exists("API_KEY.txt"):
            try:
                with open("API_KEY.txt", "r", encoding="utf-8") as f:
                    self.api_key_var.set(f.read().strip())
            except:
                pass

    def create_widgets(self):
        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

        # 1. API Key Section
        ctk.CTkLabel(self, text="DeepSeek API Key:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.api_key_entry = ctk.CTkEntry(self, textvariable=self.api_key_var, width=400, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # 1.5 Model Selection Section
        ctk.CTkLabel(self, text="Select Model:").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.model_combo = ctk.CTkComboBox(self, variable=self.model_var, values=["deepseek-chat", "deepseek-reasoner"], width=400)
        self.model_combo.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # 2. File Selection Section
        ctk.CTkLabel(self, text="Select Word File:").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.file_entry = ctk.CTkEntry(self, textvariable=self.file_path_var, width=400)
        self.file_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        ctk.CTkButton(self, text="Browse", command=self.browse_file).grid(row=2, column=2, padx=20, pady=10)

        # 3. Action Buttons
        self.start_btn = ctk.CTkButton(self, text="Start Conversion", command=self.start_thread, fg_color="green")
        self.start_btn.grid(row=3, column=1, padx=20, pady=20, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(self, text="Stop", command=self.stop_process, fg_color="red", state="disabled")
        self.stop_btn.grid(row=3, column=2, padx=20, pady=20)

        # 4. Progress/Status
        ctk.CTkLabel(self, textvariable=self.status_var).grid(row=4, column=0, columnspan=3, padx=20, pady=5)

        # 5. Log Console
        self.log_box = ctk.CTkTextbox(self, height=300)
        self.log_box.grid(row=5, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.log_box.configure(state="disabled")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if filename:
            self.file_path_var.set(filename)

    def log(self, message):
        self.after(0, lambda: self._log_impl(message))

    def _log_impl(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
    
    def update_status(self, text):
        self.after(0, lambda: self.status_var.set(text))
    
    def enable_ui(self):
        self.after(0, lambda: self._enable_ui_impl())

    def _enable_ui_impl(self):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.is_processing = False

    def start_thread(self):
        if not self.api_key_var.get():
            self.log("Error: Please enter API Key.")
            return
        if not self.file_path_var.get():
            self.log("Error: Please select a file.")
            return
        
        if self.is_processing:
            return

        self.is_processing = True
        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        threading.Thread(target=self.run_conversion, daemon=True).start()

    def stop_process(self):
        if self.is_processing:
            self.stop_event.set()
            self.log("Stopping process... please wait.")

    def run_conversion(self):
        try:
            api_key = self.api_key_var.get()
            model = self.model_var.get()
            file_path = self.file_path_var.get()
            
            # Step 1: Check Environment (Marp)
            self.update_status("Checking Environment...")
            self.log("Checking Marp CLI...")
            marp_manager = MarpManager()
            marp_exe = marp_manager.ensure_marp_cli() 
            self.log(f"Marp CLI ready: {marp_exe}")

            if self.stop_event.is_set(): raise Exception("Process stopped by user.")

            # Step 2: Load Document
            self.update_status("Loading Document...")
            self.log(f"Loading document: {file_path}")
            loader = DocLoader(file_path)
            markdown_text = loader.load_document()
            self.log("Document loaded and text extracted.")
            
            if self.stop_event.is_set(): raise Exception("Process stopped by user.")

            # Step 3: LLM Processing
            self.update_status(f"Processing with LLM ({model})...")
            # 修复：将 GUI 显示名称映射为真实的模型 ID
            MODEL_MAPPING = {
                "deepseek-chat": "deepseek-chat",
                "deepseek-reasoner": "deepseek-reasoner"
            }
            model_id = MODEL_MAPPING.get(model, "deepseek-chat")
            llm_client = LLMClient(api_key, model=model_id)
            chunks = llm_client.chunk_text(markdown_text)
            self.log(f"Document split into {len(chunks)} chunks.")
            
            marp_chunks_list = []
            for i, chunk in enumerate(chunks):
                if self.stop_event.is_set(): raise Exception("Process stopped by user.")
                
                self.log(f"Processing chunk {i+1}/{len(chunks)}...")
                marp_chunk = llm_client.generate_marp_content(chunk)
                marp_chunks_list.append(marp_chunk)
            
            # 修复：使用 join 拼接，确保最后一个块后面没有多余的 --- 
            full_marp_content = "\n\n---\n\n".join(marp_chunks_list)
            
            # Step 4: Generate PPTX
            self.update_status("Generating PPTX...")
            self.log("Generating PPTX file...")
            
            output_file = os.path.splitext(file_path)[0] + "_converted.pptx"
            generator = PPTGenerator()
            
            success, msg = generator.generate_pptx(full_marp_content, output_file)
            
            if success:
                self.log(f"Success! PPTX saved to: {output_file}")
                self.update_status("Completed Successfully")
            else:
                self.log(f"Failed to generate PPTX: {msg}")
                self.update_status("Failed")

        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.update_status("Error Occurred")
        finally:
            self.enable_ui()


if __name__ == "__main__":
    app = App()
    app.mainloop()
