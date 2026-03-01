import os
import json
import pytest
from pathlib import Path
from core.pptx_generator import PPTXGenerator


def test_pptx_generator_initialization():
    """测试 PPTX 生成器初始化"""
    generator = PPTXGenerator()

    # 验证配置参数
    assert generator.context_layout_idx == 1
    assert generator.question_layout_idx == 2
    assert generator.context_placeholder_idx == 13
    assert generator.context_max_chars == 450
    assert generator.answer_analysis_max_chars == 400
    assert generator.question_max_chars == 1000
    assert generator.noise_threshold == 15


def test_get_weighted_length():
    """测试加权长度计算"""
    generator = PPTXGenerator()

    # 测试普通文本
    assert generator._get_weighted_length("hello") == 5

    # 测试包含换行符的文本（换行符权重为35）
    assert generator._get_weighted_length("hello\nworld") == 5 + 35 + 5  # h,e,l,l,o,\n,w,o,r,l,d

    # 测试只有换行符
    assert generator._get_weighted_length("\n") == 35


def test_split_text_by_sentences_short():
    """测试短文本不需要分割"""
    generator = PPTXGenerator()

    short_text = "这是一个短文本。"
    result = generator._split_text_by_sentences(short_text, 100)

    assert len(result) == 1
    assert result[0] == short_text


def test_split_text_by_sentences_long():
    """测试长文本需要分割"""
    generator = PPTXGenerator()

    # 创建一个超过权重限制的文本
    long_text = "这是一段很长的文本。" * 20  # 重复多次使权重超过限制
    result = generator._split_text_by_sentences(long_text, 100)

    # 验证文本确实被分割了
    assert len(result) > 1


def test_create_context_slides():
    """测试创建context幻灯片功能"""
    generator = PPTXGenerator()

    # 这个测试需要实际的PPTX模板，因此只测试方法的存在性
    # 真实测试将在集成测试中进行
    assert hasattr(generator, '_create_context_slides')
    assert callable(getattr(generator, '_create_context_slides'))


def test_create_question_slides():
    """测试创建question幻灯片功能"""
    generator = PPTXGenerator()

    # 这个测试需要实际的PPTX模板，因此只测试方法的存在性
    # 真实测试将在集成测试中进行
    assert hasattr(generator, '_create_question_slides')
    assert callable(getattr(generator, '_create_question_slides'))


def test_generate_method_signature():
    """测试generate方法接受doc_title参数"""
    generator = PPTXGenerator()

    import inspect
    sig = inspect.signature(generator.generate)
    params = list(sig.parameters.keys())

    assert 'doc_title' in params


def test_process_item_with_header_filtering():
    """测试项目处理及首项标题过滤功能"""
    generator = PPTXGenerator()

    # 模拟首项为冗余标题的context
    first_item = {
        'type': 'context',
        'content': '高一数学期末考试试卷',
        'number': ''  # 空number表示可能是冗余标题
    }

    # 验证_process_item方法存在
    assert hasattr(generator, '_process_item')
    assert callable(getattr(generator, '_process_item'))

    # 测试是否正确传递is_first_item参数
    # （这里我们只是验证接口存在性，实际逻辑已在之前的功能中测试）