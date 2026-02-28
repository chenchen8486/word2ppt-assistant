import json
from pathlib import Path
from pptx import Presentation
from typing import List, Dict, Any


class PPTXGenerator:
    """
    基于模板驱动的PPTX生成器
    使用python-pptx库，根据预定义的template.pptx模板生成PPTX文件
    """

    def __init__(self):
        # 配置参数
        self.context_layout_idx = 1  # Context专用布局
        self.question_layout_idx = 2  # Question综合专用布局

        self.context_placeholder_idx = 13  # Context专用文本框

        self.question_content_idx = 13   # 题干框
        self.question_answer_idx = 14    # 答案框
        self.question_analysis_idx = 15  # 解析框

        self.context_max_chars = 450  # Context最大字符数
        self.answer_analysis_max_chars = 400  # Answer/Analysis最大字符数

        self.noise_threshold = 15  # 智能降噪阈值

    def _split_text_by_sentences(self, text: str, max_chars: int) -> List[str]:
        """
        按句子边界精确分割文本

        Args:
            text: 输入文本
            max_chars: 最大字符数

        Returns:
            按句子边界分割后的文本列表
        """
        if len(text) <= max_chars:
            return [text]

        # 定义句子结束符
        sentence_endings = ['。', '！', '？', '.', '!', '?', '\n']

        # 找到所有句子结束位置
        positions = []
        for i, char in enumerate(text):
            if char in sentence_endings:
                positions.append(i + 1)  # 包含标点符号

        # 按最大字符数限制组合句子
        chunks = []
        start = 0

        for pos in positions:
            # 检查当前句子加入后是否会超过限制
            if pos - start > max_chars:
                # 如果当前句子本身就超过限制，不得不在此处分割
                if pos - start > max_chars and start != 0:
                    # 先添加前面的部分
                    chunk = text[start:pos].strip()
                    if chunk:
                        chunks.append(chunk)
                    start = pos
                else:
                    # 查找最佳分割点（尽可能靠近最大字符数限制，但在句子边界）
                    best_pos = pos
                    while best_pos > start and len(text[start:best_pos]) > max_chars:
                        # 从当前位置向前搜索下一个句子边界
                        prev_sentence_pos = -1
                        for p in reversed(positions):
                            if start < p < best_pos:
                                prev_sentence_pos = p
                                break

                        if prev_sentence_pos != -1 and prev_sentence_pos != start:
                            best_pos = prev_sentence_pos
                            break
                        else:
                            # 如果找不到合适的句子边界，只能在最大字符数处分割
                            best_pos = start + max_chars
                            break

                    chunk = text[start:best_pos].strip()
                    if chunk:
                        chunks.append(chunk)
                    start = best_pos

        # 处理剩余部分
        if start < len(text):
            remaining = text[start:].strip()
            if len(remaining) > max_chars:
                # 如果剩余部分仍超过限制，按字符数继续分割
                for i in range(0, len(remaining), max_chars):
                    chunks.append(remaining[i:i + max_chars])
            else:
                chunks.append(remaining)

        return chunks

    def _fill_placeholder_safe(self, slide, placeholder_idx: int, text: str):
        """
        安全地填充占位符，如果占位符不存在则打印警告

        Args:
            slide: 幻灯片对象
            placeholder_idx: 占位符索引
            text: 要填充的文本
        """
        try:
            # 尝试通过遍历占位符找到匹配的索引
            found = False
            for shape in slide.shapes:
                if hasattr(shape, 'placeholder_format') and shape.placeholder_format.idx == placeholder_idx:
                    shape.text = text
                    found = True
                    break

            if not found:
                print(f"Warning: Placeholder with idx={placeholder_idx} not found in slide")
        except Exception as e:
            print(f"Warning: Failed to fill placeholder {placeholder_idx}: {str(e)}")

    def _create_context_slides(self, prs, content: str):
        """
        为context内容创建幻灯片，处理长文本分页

        Args:
            prs: Presentation对象
            content: 要渲染的内容
        """
        # 按句子分割长文本
        content_chunks = self._split_text_by_sentences(content, self.context_max_chars)

        for chunk in content_chunks:
            # 创建新幻灯片
            slide = prs.slides.add_slide(prs.slide_layouts[self.context_layout_idx])

            # 安全填充占位符
            self._fill_placeholder_safe(slide, self.context_placeholder_idx, chunk)

    def _create_question_slides(self, prs, content: str, answer: str, analysis: str):
        """
        为question内容创建幻灯片，处理长文本分页

        Args:
            prs: Presentation对象
            content: 题干内容
            answer: 答案内容
            analysis: 解析内容
        """
        # 获取需要分割的内容
        content_chunks = self._split_text_by_sentences(content, self.context_max_chars)
        answer_chunks = self._split_text_by_sentences(answer, self.answer_analysis_max_chars) if answer else ['']
        analysis_chunks = self._split_text_by_sentences(analysis, self.answer_analysis_max_chars) if analysis else ['']

        # 创建初始幻灯片
        slide = prs.slides.add_slide(prs.slide_layouts[self.question_layout_idx])

        # 填充第一块内容到初始幻灯片
        first_content = content_chunks.pop(0) if content_chunks else ''
        first_answer = answer_chunks.pop(0) if answer_chunks else ''
        first_analysis = analysis_chunks.pop(0) if analysis_chunks else ''

        self._fill_placeholder_safe(slide, self.question_content_idx, first_content)
        if first_answer:
            self._fill_placeholder_safe(slide, self.question_answer_idx, first_answer)
        if first_analysis:
            self._fill_placeholder_safe(slide, self.question_analysis_idx, first_analysis)

        # 创建额外的幻灯片来承载剩余内容
        all_remaining = []

        # 添加剩余的内容块
        for chunk in content_chunks:
            all_remaining.append(('content', chunk))

        # 添加剩余的答案块
        for chunk in answer_chunks:
            all_remaining.append(('answer', chunk))

        # 添加剩余的解析块
        for chunk in analysis_chunks:
            all_remaining.append(('analysis', chunk))

        # 为每个剩余块创建新幻灯片
        for item_type, chunk in all_remaining:
            new_slide = prs.slides.add_slide(prs.slide_layouts[self.question_layout_idx])

            # 只填充当前类型的文本，其他保持为空
            if item_type == 'content':
                self._fill_placeholder_safe(new_slide, self.question_content_idx, chunk)
            elif item_type == 'answer':
                self._fill_placeholder_safe(new_slide, self.question_answer_idx, chunk)
            elif item_type == 'analysis':
                self._fill_placeholder_safe(new_slide, self.question_analysis_idx, chunk)

    def generate(self, json_path: str, template_path: str, output_path: str) -> bool:
        """
        生成PPTX文件的核心方法

        Args:
            json_path: 输入的JSON文件路径（Phase 2生成的数据）
            template_path: 模板PPTX文件路径
            output_path: 输出PPTX文件路径

        Returns:
            是否成功生成
        """
        try:
            # 加载JSON数据
            with open(json_path, 'r', encoding='utf-8-sig') as f:
                extracted_data = json.load(f)

            # 加载模板
            prs = Presentation(template_path)

            # 遍历所有条目
            for item_or_list in extracted_data:
                if isinstance(item_or_list, list):
                    # 如果是列表，遍历其中的每个项目
                    for item in item_or_list:
                        self._process_item(prs, item)
                elif isinstance(item_or_list, dict):
                    # 如果是字典，直接处理
                    self._process_item(prs, item_or_list)

            # 保存PPTX文件
            prs.save(output_path)
            print(f"Successfully saved PPTX to {output_path}")
            return True

        except Exception as e:
            print(f"Error generating PPTX: {str(e)}")
            return False

    def _process_item(self, prs, item: Dict[str, Any]):
        """
        处理单个项目

        Args:
            prs: Presentation对象
            item: 数据项
        """
        if not isinstance(item, dict):
            return

        # 检查是否是错误项
        if 'error' in item:
            # 跳过错误项
            print(f"Skipping error item: {item.get('error', 'Unknown error')}")
            return

        # 检查是否缺少必要的字段
        if 'type' not in item:
            return

        item_type = item.get('type', '').lower()

        if item_type == 'context':
            content = item.get('content', '')

            # 智能降噪：如果内容长度小于阈值，跳过
            if len(content.strip()) < self.noise_threshold:
                print(f"Skipping short context: '{content[:50]}...' (length: {len(content)})")
                return

            # 创建context幻灯片
            self._create_context_slides(prs, content)

        elif item_type == 'question':
            content = item.get('content', '')
            answer = item.get('answer', '')
            analysis = item.get('analysis', '')

            # 创建question幻灯片
            self._create_question_slides(prs, content, answer, analysis)


if __name__ == "__main__":
    # 测试代码
    generator = PPTXGenerator()
    success = generator.generate(
        json_path="data/02_temp_build/test_extracted.json",
        template_path="data/template.pptx",
        output_path="data/03_output_pptx/test_output.pptx"
    )
    print(f"Generation {'successful' if success else 'failed'}")