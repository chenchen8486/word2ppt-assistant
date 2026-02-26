import os
import threading
import queue
from pathlib import Path
from typing import Callable, Optional
from utils.doc_loader import extract_document_content
from core.chunk_manager import ChunkManager
from core.llm_client import LLMClient
from core.marp_renderer import MarpRenderer


class BatchProcessor:
    """
    批量处理器
    扫描输入目录并处理所有 .docx 文件
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None, model_name: str = None):
        self.log_callback = log_callback
        self.should_stop = False
        self.model_name = model_name
        self.client = None  # 延迟初始化 LLM 客户端

    def log(self, message: str):
        """记录日志"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def process_single_file(self, file_path: str):
        """
        处理单个文件的完整工作流

        Args:
            file_path: 输入的 .docx 文件路径
        """
        try:
            file_name = Path(file_path).stem
            self.log(f"开始处理文件: {file_name}")

            # Phase 1: 文档解析
            self.log(f"[Phase 1] 解析文档: {file_name}")
            extraction_result = extract_document_content(file_path)
            markdown_path = extraction_result['markdown_file_path']
            self.log(f"✓ 文档解析完成: {markdown_path}")

            # Phase 2: 分块处理
            self.log(f"[Phase 2] 分块处理: {file_name}")
            chunk_manager = ChunkManager()
            chunk_result = chunk_manager.process_markdown_file(markdown_path)
            chunks_path = chunk_result['output_path']
            self.log(f"✓ 分块处理完成: {chunks_path}")

            # 延迟初始化 LLM 客户端
            if self.client is None:
                self.client = LLMClient(model_name=self.model_name)

            # Phase 3: LLM 提取
            self.log(f"[Phase 3] LLM 结构化提取: {file_name}")
            # 由于异步处理，我们需要使用 asyncio
            import asyncio
            extracted_result = asyncio.run(
                self.client.process_chunks_file(chunks_path)
            )
            extracted_path = extracted_result['output_path']
            self.log(f"✓ LLM 提取完成: {extracted_path}")

            # Phase 3: 渲染为 Marp
            self.log(f"[Phase 3] 渲染为 Marp: {file_name}")
            renderer = MarpRenderer()
            final_md_path = renderer.render_from_file(extracted_path)
            self.log(f"✓ Marp 渲染完成: {final_md_path}")

            # Phase 3: 转换为 PPTX
            self.log(f"[Phase 3] 转换为 PPTX: {file_name}")
            renderer = MarpRenderer()  # 重新创建渲染器实例
            pptx_path = renderer.convert_to_pptx(final_md_path)
            if pptx_path:
                self.log(f"✓ PPTX 转换完成: {pptx_path}")
            else:
                self.log(f"✗ PPTX 转换失败: {file_name}")

            self.log(f"✓ 文件处理完成: {file_name}")

        except Exception as e:
            self.log(f"✗ 处理文件时出错 {file_path}: {str(e)}")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}")

    def scan_and_process(self, input_dir: str = "data/01_input_docs"):
        """
        扫描输入目录并处理所有 .docx 文件

        Args:
            input_dir: 输入目录路径
        """
        if not os.path.exists(input_dir):
            self.log(f"输入目录不存在: {input_dir}")
            return

        # 查找所有 .docx 文件
        docx_files = list(Path(input_dir).glob("*.docx"))

        if not docx_files:
            self.log(f"在 {input_dir} 中未找到 .docx 文件")
            return

        self.log(f"发现 {len(docx_files)} 个 .docx 文件待处理")

        # 逐个处理文件
        for i, file_path in enumerate(docx_files):
            if self.should_stop:
                self.log("处理被用户中断")
                break

            self.log(f"处理进度: {i+1}/{len(docx_files)} - {file_path.name}")
            self.process_single_file(str(file_path))

        self.log("批量处理完成")

    def stop_processing(self):
        """停止处理"""
        self.should_stop = True


class AsyncBatchProcessor:
    """
    异步批量处理器
    使用线程运行批处理任务，防止阻塞 UI
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None, model_name: str = None):
        self.processor = BatchProcessor(log_callback, model_name)
        self.thread = None
        self.is_running = False

    def start_processing(self, input_dir: str = "data/01_input_docs"):
        """启动批处理任务"""
        if self.is_running:
            return

        self.is_running = True
        self.thread = threading.Thread(
            target=self._run_processing,
            args=(input_dir,),
            daemon=True
        )
        self.thread.start()

    def _run_processing(self, input_dir: str):
        """在线程中运行处理任务"""
        try:
            self.processor.scan_and_process(input_dir)
        finally:
            self.is_running = False

    def stop_processing(self):
        """停止批处理"""
        self.processor.stop_processing()
        self.is_running = False