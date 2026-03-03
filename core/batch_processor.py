import os
import threading
import queue
from pathlib import Path
from typing import Callable, Optional
from utils.doc_loader import extract_document_content
from core.chunk_manager import ChunkManager
from core.llm_client import LLMClient
from core.pptx_generator import PPTXGenerator


class BatchProcessor:
    """
    批量处理器
    扫描输入目录并处理所有 .docx 文件
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None, model_name: str = None, keep_temp_files: bool = False, dev_mode: bool = False):
        self.log_callback = log_callback
        self.should_stop = False
        self.model_name = model_name
        self.keep_temp_files = keep_temp_files  # 新增参数：是否保留临时文件
        self.dev_mode = dev_mode  # 新增参数：开发者模式
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

            # 用户模式下只显示简洁日志
            if self.dev_mode:
                self.log(f"▶ 正在处理: {file_name}")
            else:
                self.log(f"▶ 正在处理: {file_name}")

            # Phase 1: 文档解析
            if self.dev_mode:
                self.log(f"[Phase 1] 解析文档: {file_name}")
            else:
                self.log(f"⏳ 正在分析文档内容...")

            extraction_result = extract_document_content(file_path)
            markdown_path = extraction_result['markdown_file_path']

            if self.dev_mode:
                self.log(f"✓ 文档解析完成: {markdown_path}")

            # Phase 2: 分块处理
            if self.dev_mode:
                self.log(f"[Phase 2] 分块处理: {file_name}")
            chunk_manager = ChunkManager()
            chunk_result = chunk_manager.process_markdown_file(markdown_path)
            chunks_path = chunk_result['output_path']

            if self.dev_mode:
                self.log(f"✓ 分块处理完成: {chunks_path}")

            # 延迟初始化 LLM 客户端
            if self.client is None:
                self.client = LLMClient(model_name=self.model_name)

            # Phase 3: LLM 提取
            if self.dev_mode:
                self.log(f"[Phase 3] LLM 结构化提取: {file_name}")
            else:
                self.log(f"⏳ 正在进行 AI 结构化排版 (耗时较长，请耐心等待)...")

            # 由于异步处理，我们需要使用 asyncio
            import asyncio
            extracted_result = asyncio.run(
                self.client.process_chunks_file(chunks_path)
            )
            extracted_path = extracted_result['output_path']

            if self.dev_mode:
                self.log(f"✓ LLM 提取完成: {extracted_path}")

            # Phase 3: 渲染为 PPTX
            if self.dev_mode:
                self.log(f"[Phase 3] 渲染为 PPTX: {file_name}")
            else:
                self.log(f"⏳ 正在生成 PPTX 文件...")

            # 生成输出路径
            output_dir = Path("data/03_output_pptx")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{file_name}.pptx"

            # 创建PPTX生成器并生成文件
            generator = PPTXGenerator()
            success = generator.generate(
                json_path=extracted_path,
                output_path=str(output_path),
                doc_title=file_name  # Pass the document title
            )

            if success:
                if self.dev_mode:
                    self.log(f"✓ PPTX 生成完成: {output_path}")

                # 无论开发者模式与否，都显示清晰的成功信息
                self.log(f"")
                self.log(f"✅ 成功: {file_name} 转换完毕！")
                self.log(f"--------------------------------------------------")
            else:
                # 显示友好的错误信息
                error_msg = f"❌ 失败: {file_name} - PPTX 生成失败"
                if self.dev_mode:
                    error_msg += f" (路径: {output_path})"
                self.log(error_msg)
                self.log(f"--------------------------------------------------")

            # 根据keep_temp_files参数决定是否清理临时文件
            if not self.keep_temp_files:
                # 删除中间文件
                try:
                    if Path(chunks_path).exists():
                        Path(chunks_path).unlink()
                        if self.dev_mode:
                            self.log(f"已删除中间文件: {chunks_path}")

                    if Path(extracted_path).exists():
                        Path(extracted_path).unlink()
                        if self.dev_mode:
                            self.log(f"已删除中间文件: {extracted_path}")

                    # 删除原始markdown文件
                    if Path(markdown_path).exists() and "temp_build" in str(markdown_path):
                        Path(markdown_path).unlink()
                        if self.dev_mode:
                            self.log(f"已删除中间文件: {markdown_path}")

                except Exception as e:
                    if self.dev_mode:
                        self.log(f"删除中间文件时出现错误: {str(e)}")

        except Exception as e:
            # 错误处理：在用户模式下显示友好信息，在开发者模式下显示详细信息
            file_name = Path(file_path).stem
            if self.dev_mode:
                # 开发者模式显示详细错误
                self.log(f"✗ 处理文件时出错 {file_path}: {str(e)}")
                import traceback
                self.log(f"错误详情: {traceback.format_exc()}")
            else:
                # 用户模式显示友好错误
                self.log(f"❌ 失败: {file_name} - 处理时发生错误: {str(e)}")
                self.log(f"--------------------------------------------------")

    def scan_and_process(self, input_dir: str = None):
        """
        扫描输入目录并处理所有 .docx 文件

        Args:
            input_dir: 输入目录路径，如果为None则使用默认路径
        """
        # 如果没有指定输入目录，则尝试从配置中获取上次使用的路径，否则使用默认路径
        if input_dir is None:
            from utils.config_manager import ConfigManager
            config_manager = ConfigManager()
            last_input_path = config_manager.get_last_used_path("input_folder")
            if last_input_path and Path(last_input_path).exists():
                input_dir = last_input_path
            else:
                input_dir = "data/01_input_docs"

        if not os.path.exists(input_dir):
            self.log(f"输入目录不存在: {input_dir}")
            # 创建目录
            Path(input_dir).mkdir(parents=True, exist_ok=True)
            self.log(f"已创建输入目录: {input_dir}")
            return

        # 查找所有 .docx 文件
        docx_files = list(Path(input_dir).glob("*.docx"))

        if not docx_files:
            self.log(f"在 {input_dir} 中未找到 .docx 文件")
            return

        # 根据模式显示不同的信息
        if self.dev_mode:
            self.log(f"发现 {len(docx_files)} 个 .docx 文件待处理")
        else:
            self.log(f"开始处理 {len(docx_files)} 个 Word 文档...")

        # 逐个处理文件
        for i, file_path in enumerate(docx_files):
            if self.should_stop:
                self.log("处理被用户中断")
                break

            # 根据模式显示不同的进度信息
            if self.dev_mode:
                self.log(f"处理进度: {i+1}/{len(docx_files)} - {file_path.name}")
            else:
                self.log(f"正在处理: {file_path.name}")

            self.process_single_file(str(file_path))

        # 显示批量处理完成信息
        if self.dev_mode:
            self.log("批量处理完成")
        else:
            self.log(f"")
            self.log(f"🎉 批量转换任务全部完成！")
            self.log(f"==================================================")

    def stop_processing(self):
        """停止处理"""
        self.should_stop = True


class AsyncBatchProcessor:
    """
    异步批量处理器
    使用线程运行批处理任务，防止阻塞 UI
    """

    def __init__(self, log_callback: Optional[Callable[[str], None]] = None, model_name: str = None, keep_temp_files: bool = False, dev_mode: bool = False):
        self.processor = BatchProcessor(log_callback, model_name, keep_temp_files, dev_mode)
        self.thread = None
        self.is_running = False

    def start_processing(self, input_dir: str = None):
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