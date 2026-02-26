import json
import subprocess
import os
from pathlib import Path
from typing import List, Dict, Any


class MarpRenderer:
    """
    基于 JSON 的 Marp 渲染引擎
    将结构化的试题数据转换为 Marp Markdown 文件
    """

    def __init__(self):
        # 定义全局样式
        self.marp_header = """---
marp: true
theme: default
paginate: true
---

<style>
/* 全局字体设置 */
section {
    font-family: 'Microsoft YaHei', 'SimSun', serif;
}

/* 大题背景文字样式 */
.context-text {
    font-size: 20px;
    line-height: 1.5;
    color: #555;
}

/* 小题文字样式 */
.question-text {
    font-size: 28px;
    line-height: 1.6;
    color: #333;
}

/* 答案和解析强调样式 */
.answer-highlight {
    color: #e74c3c;
    font-weight: bold;
}

.analysis-highlight {
    color: #27ae60;
    font-weight: bold;
}

/* 防止内容溢出 */
.content-box {
    max-width: 100%;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

/* 页面分隔符样式 */
.page-break {
    page-break-before: always;
}
</style>
"""

        # 字数限制设置
        self.max_context_chars = 400  # context 最大字符数
        self.max_analysis_chars = 600  # analysis 最大字符数

    def _split_text_if_needed(self, text: str, max_chars: int) -> List[str]:
        """
        如果文本超过指定字符数，则分割文本

        Args:
            text: 输入文本
            max_chars: 最大字符数

        Returns:
            分割后的文本列表
        """
        if len(text) <= max_chars:
            return [text]

        # 按句子或词语分割，避免在单词中间切断
        chunks = []
        current_chunk = ""

        # 按段落分割优先
        paragraphs = text.split('\n\n')

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_chars:
                if current_chunk:
                    current_chunk += '\n\n' + paragraph
                else:
                    current_chunk = paragraph
            else:
                # 如果当前块已有内容，先保存它
                if current_chunk:
                    chunks.append(current_chunk)

                # 如果段落本身超过限制，按句子分割
                if len(paragraph) > max_chars:
                    # 按句号、问号、感叹号分割句子
                    sentences = []
                    sentence = ""
                    for char in paragraph:
                        sentence += char
                        if char in ['。', '！', '？', '.', '!', '?', '\n']:
                            sentences.append(sentence)
                            sentence = ""

                    # 如果还有未完成的句子
                    if sentence.strip():
                        sentences.append(sentence)

                    temp_chunk = ""
                    for sentence in sentences:
                        if len(temp_chunk) + len(sentence) <= max_chars:
                            temp_chunk += sentence
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = sentence

                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = paragraph

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _render_context(self, context_item: Dict[str, Any]) -> str:
        """
        渲染 context 类型的内容

        Args:
            context_item: 包含 context 数据的字典

        Returns:
            渲染后的 Markdown 字符串
        """
        content = context_item.get('content', '')

        # 检查是否需要分割
        content_chunks = self._split_text_if_needed(content, self.max_context_chars)

        rendered_parts = []
        for i, chunk in enumerate(content_chunks):
            # 替换图片引用
            chunk_with_images = self._replace_image_references(chunk, context_item.get('images', []))

            # 渲染当前块
            rendered_parts.append(f'<div class="context-text">{chunk_with_images}</div>')

            # 如果不是最后一块，添加分页符
            if i < len(content_chunks) - 1:
                rendered_parts.append('\n---\n')

        return '\n'.join(rendered_parts)

    def _render_question(self, question_item: Dict[str, Any]) -> str:
        """
        渲染 question 类型的内容

        Args:
            question_item: 包含 question 数据的字典

        Returns:
            渲染后的 Markdown 字符串
        """
        number = question_item.get('number', '')
        content = question_item.get('content', '')
        answer = question_item.get('answer', '')
        analysis = question_item.get('analysis', '')

        # 第一页：题干
        content_with_images = self._replace_image_references(content, question_item.get('images', []))

        first_page = f"## {number}. {content_with_images}"

        # 第二页：题干 + 答案 + 解析
        second_page_parts = [f"## {number}. {content_with_images}"]

        if answer:
            second_page_parts.append(f'\n<br/>\n**<span class="answer-highlight">【答案】</span>** {answer}')

        if analysis:
            # 检查分析是否需要分割
            analysis_chunks = self._split_text_if_needed(analysis, self.max_analysis_chars)
            for i, chunk in enumerate(analysis_chunks):
                if i == 0:
                    second_page_parts.append(f'\n<br/>\n**<span class="analysis-highlight">【解析】</span>** {chunk}')
                else:
                    # 如果分析太长，分割到新页面
                    second_page_parts.extend(['\n---', f'**<span class="analysis-highlight">【解析】(续)</span>** {chunk}'])

        second_page = '\n'.join(second_page_parts)

        return f"{first_page}\n\n---\n\n{second_page}"

    def _replace_image_references(self, text: str, images: List[str]) -> str:
        """
        替换文本中的图片引用

        Args:
            text: 原始文本
            images: 图片路径列表

        Returns:
            替换了图片引用的文本
        """
        result_text = text
        for img_path in images:
            img_name = Path(img_path).name
            # 使用相对路径
            relative_path = f"../{img_path}"
            # 替换为 Marp 图片语法
            result_text = result_text.replace(img_name, f'![width:800px]({relative_path})')

        return result_text

    def render_from_json(self, extracted_data: List[Dict[str, Any]]) -> str:
        """
        从 JSON 数据渲染完整的 Marp Markdown

        Args:
            extracted_data: 提取的结构化数据

        Returns:
            完整的 Marp Markdown 字符串
        """
        # 添加 Marp 头部
        markdown_content = self.marp_header

        # 遍历 JSON 数组，按顺序渲染
        # 注意：extracted_data 中的每一项可能是一个列表（来自一个 chunk 的多个项目）
        for item_or_list in extracted_data:
            if isinstance(item_or_list, list):
                # 如果是列表，说明是单个 chunk 的结果，遍历其中的每个项目
                for item in item_or_list:
                    # 检查是否是错误项
                    if isinstance(item, dict) and 'error' in item:
                        error_msg = item.get('error', 'Unknown error')
                        original_content = item.get('original_chunk', {}).get('content', '')[:200]  # 只取前200字符
                        markdown_content += f"\n<!-- 处理错误: {error_msg} -->\n<div class=\"context-text\">原始内容片段: {original_content}...</div>\n"
                        continue

                    if isinstance(item, dict):
                        item_type = item.get('type', '').lower()
                        if item_type == 'context':
                            markdown_content += f"\n{self._render_context(item)}\n"
                        elif item_type == 'question':
                            markdown_content += f"\n{self._render_question(item)}\n"
                        else:
                            # 未知类型，尝试作为题目处理
                            markdown_content += f"\n{self._render_question(item)}\n"
            elif isinstance(item_or_list, dict):
                # 如果是字典，检查是否是错误项
                if 'error' in item_or_list:
                    error_msg = item_or_list.get('error', 'Unknown error')
                    original_content = item_or_list.get('original_chunk', {}).get('content', '')[:200]  # 只取前200字符
                    markdown_content += f"\n<!-- 处理错误: {error_msg} -->\n<div class=\"context-text\">原始内容片段: {original_content}...</div>\n"
                    continue

                item_type = item_or_list.get('type', '').lower()
                if item_type == 'context':
                    markdown_content += f"\n{self._render_context(item_or_list)}\n"
                elif item_type == 'question':
                    markdown_content += f"\n{self._render_question(item_or_list)}\n"
                else:
                    # 未知类型，尝试作为题目处理
                    markdown_content += f"\n{self._render_question(item_or_list)}\n"

        return markdown_content

    def render_from_file(self, json_file_path: str, output_dir: str = "data/02_temp_build"):
        """
        从 JSON 文件渲染 Marp Markdown

        Args:
            json_file_path: 输入 JSON 文件路径
            output_dir: 输出目录

        Returns:
            输出文件路径
        """
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8-sig') as f:
            extracted_data = json.load(f)

        # 渲染 Markdown
        markdown_content = self.render_from_json(extracted_data)

        # 生成输出路径
        file_name = Path(json_file_path).stem.replace('_extracted', '')
        output_path = Path(output_dir) / f"{file_name}_final.md"

        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 保存渲染结果
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(markdown_content)

        return str(output_path)

    def convert_to_pptx(self, markdown_file_path: str, output_dir: str = "data/03_output_pptx"):
        """
        将 Markdown 文件转换为 PPTX

        Args:
            markdown_file_path: 输入 Markdown 文件路径
            output_dir: 输出目录

        Returns:
            输出 PPTX 文件路径
        """
        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 生成输出路径
        file_name = Path(markdown_file_path).stem.replace('_final', '')
        output_path = Path(output_dir) / f"{file_name}.pptx"

        # 首先尝试使用本地的 marp.exe
        marp_path = "bin/marp.exe"

        # 如果本地 marp.exe 不存在，尝试全局安装的 marp
        if not Path(marp_path).exists():
            # 尝试在 PATH 中查找 marp
            import shutil
            global_marp = shutil.which("marp")
            if global_marp:
                marp_path = global_marp
            else:
                print(f"错误：找不到 Marp 工具。请确保已安装 marp 或将 bin/marp.exe 放在正确位置。")
                return None

        # 调用 marp 命令行工具
        cmd = [
            marp_path,
            markdown_file_path,
            "-o", str(output_path),
            "--allow-local-files"  # 允许本地文件访问
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"成功将 {markdown_file_path} 转换为 {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            print(f"Marp 转换失败: {e}")
            print(f"命令: {' '.join(cmd)}")
            print(f"错误输出: {e.stderr}")
            print(f"标准输出: {e.stdout}")
            return None
        except FileNotFoundError:
            print(f"错误：找不到 Marp 工具: {marp_path}")
            print("请确保已安装并添加到 PATH 或放在 bin/ 目录下")
            return None