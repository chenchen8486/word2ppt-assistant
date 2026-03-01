import json
import re
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
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

        self.context_max_chars = 450  # Context最大字符数
        self.answer_analysis_max_chars = 400  # Answer/Analysis最大字符数
        self.question_max_chars = 600  # Question整体最大字符数（优化为600以兼容选项换行）

        self.noise_threshold = 15  # 智能降噪阈值

    def _split_text_by_sentences(self, text: str, max_chars: int = 650) -> List[str]:
        """
        按句子边界精确分割文本

        Args:
            text: 输入文本
            max_chars: 最大字符数，默认650以避免PPT排版崩溃

        Returns:
            按句子边界分割后的文本列表
        """
        if len(text) <= max_chars:
            return [text]

        # 定义句子结束符
        sentence_endings = ['。', '！', '？', '；', ';', '!', '?', '。', '\n']

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

    def _create_context_slides(self, prs, content: str, number: str = ""):
        """
        为context内容创建幻灯片，处理长文本分页

        Args:
            prs: Presentation对象
            content: 要渲染的内容
            number: 题号（可选）
        """
        # 拼接题号和内容
        if number:
            full_content = f"{number} {content}"
        else:
            full_content = content

        # 按句子分割长文本，使用650字符的足额阈值（符合零空行原则）
        content_chunks = self._split_text_by_sentences(full_content, 650)

        for chunk in content_chunks:
            # 创建新幻灯片
            slide = prs.slides.add_slide(prs.slide_layouts[self.context_layout_idx])

            # 寻找合适的文本框来填充内容
            target_shape = None
            for shape in slide.shapes:
                if hasattr(shape, 'placeholder_format') and shape.placeholder_format is not None:
                    if shape.placeholder_format.idx == self.context_placeholder_idx:
                        target_shape = shape
                        break

            # 如果找到了目标占位符，填充内容
            if target_shape and target_shape.has_text_frame:
                # 设置段落属性
                text_frame = target_shape.text_frame
                p = text_frame.paragraphs[0] if text_frame.paragraphs else text_frame.add_paragraph()
                p.text = chunk
                p.font.size = Pt(14)  # 设置字体大小为14pt
                p.font.name = '微软雅黑'  # 强制设置中文字体
                p.alignment = PP_ALIGN.LEFT  # 左对齐

    def _create_question_slides(self, prs, content: str, answer: str, analysis: str, number: str = ""):
        """
        为question内容创建幻灯片，使用单个占位符的富文本渲染，带智能分页

        Args:
            prs: Presentation对象
            content: 题干内容
            answer: 答案内容
            analysis: 解析内容
            number: 题号（可选）
        """
        # 拼接题号和题干内容
        if number:
            full_content = f"{number}. {content}"
        else:
            full_content = content

        # 先处理题干，将其按句子分割
        content_chunks = self._split_text_by_sentences(full_content, self.question_max_chars)

        # 循环处理题干chunks
        last_tf = None
        for i, chunk in enumerate(content_chunks):
            # 为第一个chunk创建幻灯片，后续的chunk也需要新的幻灯片
            slide = prs.slides.add_slide(prs.slide_layouts[self.question_layout_idx])

            # 寻找主文本框 (Body Text placeholder)
            body_shape = None
            max_size = 0

            # 首先尝试找到 Body Text 类型的占位符
            for shape in slide.shapes:
                if hasattr(shape, 'placeholder_format') and shape.placeholder_format is not None:
                    # 根据模板探测结果，Body/BODY类型的占位符是idx=13，type=2(Body Text) 或 type=1(Text)
                    if shape.placeholder_format.type == 2 or shape.placeholder_format.type == 1:  # Body Text or Text
                        body_shape = shape
                        break
                    # 如果有明确的 idx=13 的占位符，也可以作为候选
                    if hasattr(shape.placeholder_format, 'idx') and shape.placeholder_format.idx == 13:
                        body_shape = shape
                        break
                # 如果没找到Body Text，尝试找最大的占位符
                if hasattr(shape, 'placeholder_format') and shape.has_text_frame:
                    if shape.width * shape.height > max_size:
                        max_size = shape.width * shape.height
                        body_shape = shape

            # 如果没找到合适的占位符，抛出异常
            if body_shape is None or not body_shape.has_text_frame:
                raise ValueError("未能找到合适的文本占位符来渲染题目内容")

            # 获取文本框架
            tf = body_shape.text_frame

            # 清空默认文本
            tf.clear()

            # 写入题干内容（只在第一个chunk的幻灯片上）
            if i == 0:  # 第一个chunk
                p = tf.paragraphs[0]  # 获取第一个段落
                p.text = chunk
                p.font.size = Pt(14)  # 设置字体大小为14pt
                p.font.bold = False   # 正常粗细
                p.font.name = '微软雅黑'  # 强制设置中文字体
                p.alignment = PP_ALIGN.LEFT  # 左对齐
                last_tf = tf
            else:  # 后续chunks（仅当题干超长时才会出现）
                p = tf.paragraphs[0]
                p.text = chunk
                p.font.size = Pt(14)  # 设置字体大小为14pt
                p.font.bold = False
                p.font.name = '微软雅黑'  # 强制设置中文字体
                p.alignment = PP_ALIGN.LEFT  # 左对齐

        # 计算是否需要在题干后添加答案和解析
        ans_ana_len = len(answer) + len(analysis)

        # 如果有答案或解析，需要判断是否需要换页或添加到现有页
        if answer or analysis:
            # 检查最后一个幻灯片上的题干内容长度
            last_content_len = len(last_tf.paragraphs[0].text) if last_tf and last_tf.paragraphs else 0

            # 如果当前页剩余空间不足以容纳答案和解析，需要新建一页
            if last_content_len + ans_ana_len > self.question_max_chars:
                # 创建新的幻灯片来放置答案和解析
                slide = prs.slides.add_slide(prs.slide_layouts[self.question_layout_idx])

                # 寻找主文本框 (Body Text placeholder)
                body_shape = None
                max_size = 0

                # 首先尝试找到 Body Text 类型的占位符
                for shape in slide.shapes:
                    if hasattr(shape, 'placeholder_format') and shape.placeholder_format is not None:
                        if shape.placeholder_format.type == 2:  # Body Text
                            body_shape = shape
                            break
                    # 如果没找到Body Text，尝试找最大的占位符
                    if hasattr(shape, 'placeholder_format') and shape.has_text_frame:
                        if shape.width * shape.height > max_size:
                            max_size = shape.width * shape.height
                            body_shape = shape

                # 如果没找到合适的占位符，抛出异常
                if body_shape is None or not body_shape.has_text_frame:
                    raise ValueError("未能找到合适的文本占位符来渲染题目内容")

                # 获取文本框架
                last_tf = body_shape.text_frame

                # 清空默认文本
                last_tf.clear()

                # 写入题干内容（作为延续）
                p = last_tf.paragraphs[0]  # 获取第一个段落
                p.text = "[内容续]"  # 添加提示
                p.font.size = Pt(14)  # 设置字体大小为14pt
                p.font.bold = False   # 正常粗细
                p.font.name = '微软雅黑'  # 强制设置中文字体
                p.alignment = PP_ALIGN.LEFT  # 左对齐

            # 添加答案（如果存在）
            if answer:
                answer_p = last_tf.add_paragraph()  # 添加新段落
                answer_p.text = f"【答案】{answer}"  # 移除\n前缀以符合零空行原则
                answer_p.font.size = Pt(14)  # 设置字体大小为14pt
                answer_p.font.bold = True    # 加粗
                answer_p.font.color.rgb = RGBColor(220, 53, 69)  # 红色
                answer_p.font.name = '微软雅黑'  # 强制设置中文字体
                answer_p.alignment = PP_ALIGN.LEFT  # 左对齐

            # 处理解析（如果存在）
            if analysis:
                # 检查是否需要进一步拆分分析
                analysis_chunks = self._split_text_by_sentences(analysis, self.question_max_chars)

                for j, ana_chunk in enumerate(analysis_chunks):
                    analysis_p = last_tf.add_paragraph()  # 添加新段落
                    if j == 0:
                        analysis_p.text = f"【解析】{ana_chunk}"  # 移除\n前缀以符合零空行原则
                    else:
                        analysis_p.text = f"[解析续]{ana_chunk}"

                    analysis_p.font.size = Pt(14)  # 设置字体大小为14pt
                    analysis_p.font.bold = False   # 正常粗细
                    analysis_p.font.color.rgb = RGBColor(40, 167, 69)  # 绿色
                    analysis_p.font.name = '微软雅黑'  # 强制设置中文字体
                    analysis_p.alignment = PP_ALIGN.LEFT  # 左对齐

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
            number = item.get('number', '')  # 提取题号

            # 智能降噪：如果内容长度小于阈值，跳过
            if len(content.strip()) < self.noise_threshold:
                print(f"Skipping short context: '{content[:50]}...' (length: {len(content)})")
                return

            # 文本净化：压缩连续换行符
            content = re.sub(r'\n\s*\n', '\n', content).strip()

            # 创建context幻灯片
            self._create_context_slides(prs, content, number)

        elif item_type == 'question':
            content = item.get('content', '')
            answer = item.get('answer', '')
            analysis = item.get('analysis', '')
            number = item.get('number', '')  # 提取题号

            # 文本净化：压缩连续换行符
            content = re.sub(r'\n\s*\n', '\n', content).strip()
            if answer:
                answer = re.sub(r'\n\s*\n', '\n', answer).strip()
            if analysis:
                analysis = re.sub(r'\n\s*\n', '\n', analysis).strip()

            # 创建question幻灯片
            self._create_question_slides(prs, content, answer, analysis, number)


if __name__ == "__main__":
    # 测试代码
    generator = PPTXGenerator()
    success = generator.generate(
        json_path="data/02_temp_build/test_extracted.json",
        template_path="data/template.pptx",
        output_path="data/03_output_pptx/test_output.pptx"
    )
    print(f"Generation {'successful' if success else 'failed'}")