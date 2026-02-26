import os
import json
import pytest
from pathlib import Path
from core.marp_renderer import MarpRenderer


def test_marp_renderer_initialization():
    """测试 Marp 渲染器初始化"""
    renderer = MarpRenderer()

    # 验证样式头部存在
    assert renderer.marp_header is not None
    assert "marp: true" in renderer.marp_header
    assert "font-family" in renderer.marp_header

    # 验证字符限制设置
    assert renderer.max_context_chars == 400
    assert renderer.max_analysis_chars == 600


def test_split_text_if_needed_short():
    """测试短文本不需要分割"""
    renderer = MarpRenderer()

    short_text = "这是一个短文本，长度小于限制。"
    result = renderer._split_text_if_needed(short_text, 100)

    assert len(result) == 1
    assert result[0] == short_text


def test_split_text_if_needed_long():
    """测试长文本需要分割"""
    renderer = MarpRenderer()

    # 创建一个超过400字符的文本
    long_text = "这是一段很长的文本。" * 50  # 20 * 50 = 1000 字符
    result = renderer._split_text_if_needed(long_text, 400)

    # 验证文本确实被分割了
    assert len(result) > 1
    assert all(len(chunk) <= 400 for chunk in result)

    # 验证所有片段加起来等于原文本
    combined_text = "".join(result)
    assert combined_text == long_text


def test_render_context():
    """测试 context 渲染"""
    renderer = MarpRenderer()

    context_item = {
        'type': 'context',
        'content': '这是一段大题背景文字，用来描述整个题目集合的背景。',
        'images': []
    }

    result = renderer._render_context(context_item)

    # 验证包含 context 样式
    assert 'class="context-text"' in result
    assert 'font-size: 20px' in renderer.marp_header


def test_render_question():
    """测试 question 渲染"""
    renderer = MarpRenderer()

    question_item = {
        'type': 'question',
        'number': '1',
        'content': '这是一道选择题的内容。',
        'answer': 'A',
        'analysis': '这道题的解析过程如下...',
        'images': []
    }

    result = renderer._render_question(question_item)

    # 验证包含题号和内容
    assert '## 1.' in result
    assert '这是一道选择题的内容。' in result

    # 验证答案和解析标签
    assert '【答案】' in result
    assert '【解析】' in result


def test_render_from_json():
    """测试从 JSON 渲染完整 Markdown"""
    renderer = MarpRenderer()

    # 创建测试数据，包含一个超长的 context（模拟需求）
    test_data = [
        {
            'type': 'context',
            'content': '这是很长的大题背景文字。' * 200,  # 超过400字符
            'images': []
        },
        {
            'type': 'question',
            'number': '1',
            'content': '这是第一道题的内容。',
            'answer': '正确答案',
            'analysis': '这是第一道题的解析。' * 100  # 可能也会很长
        },
        {
            'type': 'question',
            'number': '2',
            'content': '这是第二道题的内容。',
            'answer': '另一个答案',
            'analysis': '这是第二道题的解析。'
        }
    ]

    result = renderer.render_from_json(test_data)

    # 验证包含 Marp 头部
    assert 'marp: true' in result

    # 验证包含分页符（因为有长文本需要分割）
    assert result.count('---') >= 2  # 至少有一个 context 分页和 question 分页

    # 验证包含题号
    assert '## 1.' in result
    assert '## 2.' in result


def test_replace_image_references():
    """测试图片引用替换"""
    renderer = MarpRenderer()

    text_with_image = "这里是题目内容，包含图片 image001.png。"
    images = ["data/02_temp_build/test_images/image001.png"]

    result = renderer._replace_image_references(text_with_image, images)

    # 验证图片被替换成 Marp 语法
    assert '![](../data/02_temp_build/test_images/image001.png)' in result or '[width:800px]' in result


def test_render_from_file():
    """测试从文件渲染"""
    renderer = MarpRenderer()

    # 创建测试 JSON 文件
    test_data = [
        {
            'type': 'context',
            'content': '测试背景文字。',
            'images': []
        },
        {
            'type': 'question',
            'number': '1',
            'content': '测试题目。',
            'answer': '测试答案',
            'analysis': '测试解析。'
        }
    ]

    test_json_path = "test_extracted.json"

    try:
        # 保存测试数据
        with open(test_json_path, 'w', encoding='utf-8-sig') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        # 渲染文件
        output_path = renderer.render_from_file(test_json_path, "test_output")

        # 验证输出文件存在
        assert os.path.exists(output_path)

        # 验证文件内容
        with open(output_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        assert 'marp: true' in content
        assert '## 1.' in content

    finally:
        # 清理测试文件
        if os.path.exists(test_json_path):
            os.remove(test_json_path)

        # 清理输出目录
        import shutil
        if os.path.exists("test_output"):
            shutil.rmtree("test_output", ignore_errors=True)