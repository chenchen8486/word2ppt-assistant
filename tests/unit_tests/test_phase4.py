import os
import json
import pytest
from pathlib import Path
from core.batch_processor import BatchProcessor, AsyncBatchProcessor


def test_batch_processor_initialization():
    """测试批量处理器初始化"""
    processor = BatchProcessor()

    assert processor is not None
    assert processor.should_stop is False


def test_scan_and_process_empty_dir():
    """测试扫描空目录"""
    import tempfile

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = BatchProcessor()

        # 扫描空目录
        processor.scan_and_process(temp_dir)

        # 应该记录未找到文件的消息


def test_process_single_file_logic():
    """测试单文件处理逻辑（模拟）"""
    # 测试函数是否存在和可调用
    processor = BatchProcessor()

    # 验证方法存在
    assert hasattr(processor, 'process_single_file')
    assert callable(getattr(processor, 'process_single_file'))

    assert hasattr(processor, 'scan_and_process')
    assert callable(getattr(processor, 'scan_and_process'))


def test_async_batch_processor():
    """测试异步批量处理器"""
    def dummy_log(msg):
        pass  # 简单的日志回调函数

    async_processor = AsyncBatchProcessor(log_callback=dummy_log)

    assert async_processor is not None
    assert async_processor.processor is not None
    assert async_processor.is_running is False


def test_stop_processing():
    """测试停止处理功能"""
    processor = BatchProcessor()

    # 初始状态
    assert processor.should_stop is False

    # 停止处理
    processor.stop_processing()
    assert processor.should_stop is True

    # 重置状态
    processor.should_stop = False


def test_async_stop_processing():
    """测试异步处理器停止功能"""
    def dummy_log(msg):
        pass

    async_processor = AsyncBatchProcessor(log_callback=dummy_log)

    # 初始状态
    assert async_processor.is_running is False

    # 停止处理
    async_processor.stop_processing()
    assert async_processor.is_running is False