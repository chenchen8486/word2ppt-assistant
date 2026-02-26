import re
import json
import os
from pathlib import Path
from typing import List, Dict, Any


class ChunkManager:
    """
    大题分块管理器
    将长文档按大题切分，避免 LLM 漏题
    """

    def __init__(self):
        # 支持的题号模式 - 包括可能的加粗标记
        self.patterns = [
            r'^\s*\*\*(\d+、)',                                    # 阿拉伯数字 + 顿号，带加粗 (如 "**1、")
            r'^\s*\*\*([一二三四五六七八九十]+、)',                 # 中文数字 + 顿号，带加粗 (如 "**一、")
            r'^\s*\*\*([一二三四五六七八九十]+、（[^）]*）)',        # 中文数字 + 顿号 + 括号，带加粗 (如 "**一、（9分）")
            r'^\s*\*\*([第][一二三四五六七八九十]+[卷章])',         # 第X卷/章，带加粗 (如 "**第一卷")
            r'^\s*\*\*([（\(][一二三四五六七八九十]+[）\)])',       # 带括号的中文数字，带加粗 (如 "**(一)")
            r'^\s*\*\*([一二三四五六七八九十]+\.)',                # 中文数字 + 点，带加粗 (如 "**一.")
            r'^\s*\*\*([一二三四五六七八九十]+（[^）]*）)',          # 中文数字 + 括号，带加粗 (如 "**一（9分）")
            r'^\s*\*\*([一二三四五六七八九十]+\.[^0-9])',          # 中文数字 + 点 + 非数字，带加粗 (如 "**一. ")
            r'^(\d+、)',                                          # 阿拉伯数字 + 顿号 (如 "1、")
            r'^([一二三四五六七八九十]+、)',                       # 中文数字 + 顿号 (如 "一、")
            r'^([一二三四五六七八九十]+、（[^）]*）)',              # 中文数字 + 顿号 + 括号 (如 "一、（9分）")
            r'^([第][一二三四五六七八九十]+[卷章])',                # 第X卷/章 (如 "第一卷")
            r'^([（\(][一二三四五六七八九十]+[）\)])',              # 带括号的中文数字 (如 "(一)")
            r'^([一二三四五六七八九十]+\.)',                      # 中文数字 + 点 (如 "一.")
            r'^([一二三四五六七八九十]+（[^）]*）)',                # 中文数字 + 括号 (如 "一（9分）")
            r'^([一二三四五六七八九十]+\.[^0-9])',                 # 中文数字 + 点 + 非数字 (如 "一. ")
        ]

    def split_by_questions(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        按题目分割文本

        Args:
            markdown_content: 原始 Markdown 内容

        Returns:
            分割后的块列表，每个块包含序号和内容
        """
        lines = markdown_content.split('\n')
        chunks = []
        current_chunk = {'number': '', 'content': ''}

        for line in lines:
            # 检查是否是新的题目开始
            is_new_question = False
            question_number = ''

            for pattern in self.patterns:
                match = re.match(pattern, line.strip())
                if match:
                    is_new_question = True
                    question_number = match.group(1)
                    break

            # 如果是新题目且不是第一个题目，则保存上一个块
            if is_new_question and current_chunk['content']:
                chunks.append({
                    'number': current_chunk['number'],
                    'content': current_chunk['content'].strip()
                })

                # 开始新的块
                current_chunk = {
                    'number': question_number,
                    'content': line + '\n'
                }
            else:
                # 添加到当前块
                current_chunk['content'] += line + '\n'

                # 如果是新题目，更新序号
                if is_new_question:
                    current_chunk['number'] = question_number

        # 添加最后一个块
        if current_chunk['content']:
            chunks.append({
                'number': current_chunk['number'],
                'content': current_chunk['content'].strip()
            })

        return chunks

    def save_chunks_to_json(self, chunks: List[Dict[str, Any]], output_path: str):
        """
        将分块结果保存为 JSON 文件

        Args:
            chunks: 分块列表
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

    def process_markdown_file(self, markdown_file_path: str, output_dir: str = "data/02_temp_build"):
        """
        处理 Markdown 文件并生成分块

        Args:
            markdown_file_path: 输入 Markdown 文件路径
            output_dir: 输出目录

        Returns:
            分块结果及输出文件路径
        """
        # 读取 Markdown 文件
        with open(markdown_file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # 分割文本
        chunks = self.split_by_questions(content)

        # 生成输出路径
        file_name = Path(markdown_file_path).stem.replace('_raw', '')
        output_path = Path(output_dir) / f"{file_name}_chunks.json"

        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 保存分块结果
        self.save_chunks_to_json(chunks, str(output_path))

        return {
            'chunks': chunks,
            'output_path': str(output_path)
        }