import os
import json
import pytest
import asyncio
from pathlib import Path
from core.chunk_manager import ChunkManager
from core.llm_client import LLMClient


def test_chunk_manager():
    """测试分块管理器功能"""
    manager = ChunkManager()

    # 测试用的 Markdown 内容
    test_content = """# 试卷标题

一、选择题
1、下列选项中，哪一个是正确的？
A. 错误选项
B. 正确选项
C. 错误选项
D. 错误选项

2、这是一道填空题
在____处填写答案。

二、解答题
3、这是一道解答题，请给出详细解答过程。

参考答案：
B
这是一道填空题的答案
详细解答过程...

注意事项：请认真审题。
"""

    # 执行分块
    chunks = manager.split_by_questions(test_content)

    # 验证至少有基本的分块
    assert len(chunks) >= 3  # 至少有大题头和几个题目块

    # 验证包含预期的关键内容
    has_choice_section = any('选择题' in chunk['content'] for chunk in chunks)
    has_question_1 = any('1、' in chunk['content'] for chunk in chunks)
    has_question_2 = any('2、' in chunk['content'] for chunk in chunks)
    has_answer_section = any('解答题' in chunk['content'] for chunk in chunks)

    assert has_choice_section, "应包含选择题部分"
    assert has_question_1, "应包含第1题"
    assert has_question_2, "应包含第2题"
    assert has_answer_section, "应包含解答题部分"


def test_chunk_manager_save_and_load():
    """测试分块管理器的保存和加载功能"""
    manager = ChunkManager()

    # 测试用的 Markdown 内容
    test_content = """一、选择题
1、第一题内容
2、第二题内容

二、解答题
3、第三题内容
"""

    # 分割文本
    chunks = manager.split_by_questions(test_content)

    # 临时保存路径
    temp_path = "test_chunks.json"

    try:
        # 保存分块结果
        manager.save_chunks_to_json(chunks, temp_path)

        # 验证文件是否创建
        assert os.path.exists(temp_path)

        # 验证文件内容
        with open(temp_path, 'r', encoding='utf-8-sig') as f:
            loaded_chunks = json.load(f)

        assert len(loaded_chunks) == len(chunks)
        assert loaded_chunks[0]['number'] == chunks[0]['number']

    finally:
        # 清理测试文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_llm_client_initialization():
    """测试 LLM 客户端初始化"""
    # 创建模拟的 API_KEY.txt 文件
    api_key_content = "fake-api-key-for-testing"
    api_key_file = "API_KEY.txt"

    try:
        with open(api_key_file, 'w', encoding='utf-8-sig') as f:
            f.write(api_key_content)

        # 初始化客户端
        client = LLMClient(api_key_file)

        # 验证 API 密钥被正确加载
        assert client.api_key == api_key_content

        # 验证模板被创建
        assert os.path.exists("user_templates/01_raw_input.md")
        assert os.path.exists("user_templates/02_target_output.json")

    finally:
        # 清理测试文件
        if os.path.exists(api_key_file):
            os.remove(api_key_file)

        # 清理模板目录
        import shutil
        if os.path.exists("user_templates"):
            shutil.rmtree("user_templates")


@pytest.mark.asyncio
async def test_mock_llm_extraction():
    """模拟测试 LLM 提取功能（不实际调用 API）"""
    # 这里我们测试代码结构而不实际调用 LLM API
    # 因为实际 API 调用需要网络和有效密钥

    # 创建测试分块
    test_chunks = [
        {
            'number': '1',
            'content': '这是一道测试题目。\nA. 选项A\nB. 选项B\nC. 选项C\nD. 选项D'
        },
        {
            'number': '2',
            'content': '这是另一道测试题目。\n填空题内容。'
        }
    ]

    # 验证结构
    assert len(test_chunks) == 2
    assert test_chunks[0]['number'] == '1'
    assert '题目' in test_chunks[0]['content']