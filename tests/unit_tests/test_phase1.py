import os
import tempfile
import pytest
from pathlib import Path
from utils.file_helper import initialize_directories
from utils.doc_loader import extract_document_content
from markitdown import MarkItDown


def test_initialize_directories():
    """测试目录初始化功能"""
    # 运行初始化函数
    initialize_directories()

    # 检查目录是否存在
    expected_dirs = [
        "data/01_input_docs",
        "data/02_temp_build",
        "data/03_output_pptx",
        "user_templates",
        "bin"
    ]

    for dir_path in expected_dirs:
        assert os.path.exists(dir_path), f"Directory {dir_path} should exist"


def test_extract_document_content():
    """测试文档内容提取功能"""
    # 创建一个真实的测试 .docx 文件
    import zipfile
    import io

    # 创建一个简单的 .docx 文件
    docx_path = "sample_test.docx"

    # 创建基本的 .docx 结构
    with zipfile.ZipFile(docx_path, 'w') as docx:
        # 添加文档 XML
        doc_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>Test document for conversion.</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''

        # 添加必需的文件
        docx.writestr("word/document.xml", doc_xml)
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
        docx.writestr("[Content_Types].xml", content_types)

        rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/_rels/document.xml.rels",
                     '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>''')

    try:
        # 运行提取功能
        result = extract_document_content(docx_path)

        # 验证返回结果的结构
        assert "markdown_content" in result
        assert "markdown_file_path" in result
        assert "image_paths" in result

        # 验证 markdown 文件是否被创建
        assert os.path.exists(result["markdown_file_path"])

        # 验证文件编码
        with open(result["markdown_file_path"], 'r', encoding='utf-8-sig') as f:
            content = f.read()
            assert content == result["markdown_content"]

    finally:
        # 清理测试文件
        if os.path.exists(docx_path):
            os.unlink(docx_path)

        # 清理输出文件
        output_md = "sample_test_raw.md"
        if os.path.exists(output_md):
            os.unlink(output_md)

        output_img_dir = "sample_test_images"
        if os.path.exists(output_img_dir):
            import shutil
            shutil.rmtree(output_img_dir, ignore_errors=True)


def test_extract_document_content_with_mock_docx():
    """使用模拟的 .docx 文件测试内容提取功能"""
    # 创建一个模拟的 .docx 文件（实际上是 ZIP 格式）
    mock_docx_path = "test_mock.docx"

    # .docx 文件本质上是 ZIP 文件，包含文档内容
    import zipfile

    # 创建一个简单的 mock docx 文件，包含一些文本内容
    with zipfile.ZipFile(mock_docx_path, 'w') as zf:
        # 添加一个简单的文档XML文件
        doc_xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:r>
                <w:t>This is a test document for conversion.</w:t>
            </w:r>
        </w:p>
    </w:body>
</w:document>'''

        # 添加到 ZIP 中适当的路径
        zf.writestr("word/document.xml", doc_xml_content)
        # 添加基本的 [Content_Types].xml
        content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
        zf.writestr("[Content_Types].xml", content_types)

        # 添加必要的目录结构
        rels_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
        zf.writestr("_rels/.rels", rels_content)
        zf.writestr("word/_rels/document.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')

    try:
        # 测试提取功能
        result = extract_document_content(mock_docx_path)

        # 验证结果
        assert "markdown_content" in result
        assert "markdown_file_path" in result
        assert "image_paths" in result

        # 验证输出文件被创建
        assert os.path.exists(result["markdown_file_path"])

        # 检查文件内容编码
        with open(result["markdown_file_path"], 'r', encoding='utf-8-sig') as f:
            content = f.read()
            assert content == result["markdown_content"]

    finally:
        # 清理测试文件
        if os.path.exists(mock_docx_path):
            os.remove(mock_docx_path)

        # 清理可能生成的输出文件
        test_output_md = "test_mock_raw.md"
        if os.path.exists(test_output_md):
            os.remove(test_output_md)

        test_image_dir = "test_mock_images"
        if os.path.exists(test_image_dir) and os.path.isdir(test_image_dir):
            import shutil
            shutil.rmtree(test_image_dir)