import os
import zipfile
from pathlib import Path
from markitdown import MarkItDown


def extract_document_content(docx_path: str, output_dir: str = "data/02_temp_build"):
    """
    解析 Word 文档内容并提取文本和图片

    Args:
        docx_path (str): Word 文档路径
        output_dir (str): 输出目录，默认为 data/02_temp_build

    Returns:
        dict: 包含文本内容和图片路径的字典
    """
    # 获取文档名称（不含扩展名）
    doc_name = Path(docx_path).stem

    # 初始化 MarkItDown
    markitdown = MarkItDown()

    # 提取文本内容
    result = markitdown.convert(docx_path)
    markdown_content = result.text_content

    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 保存原始 Markdown 内容
    markdown_file_path = output_path / f"{doc_name}_raw.md"
    with open(markdown_file_path, 'w', encoding='utf-8-sig') as f:
        f.write(markdown_content)

    # 提取图片
    image_paths = extract_images_from_docx(docx_path, output_dir, doc_name)

    return {
        "markdown_content": markdown_content,
        "markdown_file_path": str(markdown_file_path),
        "image_paths": image_paths
    }


def extract_images_from_docx(docx_path: str, output_dir: str, doc_name: str):
    """
    从 docx 文件中提取图片

    Args:
        docx_path (str): Word 文档路径
        output_dir (str): 输出目录
        doc_name (str): 文档名称

    Returns:
        list: 提取的图片路径列表
    """
    image_paths = []
    images_dir = Path(output_dir) / f"{doc_name}_images"
    images_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        # 列出所有文件
        file_list = zip_ref.namelist()

        # 查找图片文件
        for file_name in file_list:
            if file_name.startswith('word/media/') and any(file_name.lower().endswith(ext)
                for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif']):

                # 提取图片到指定目录
                image_filename = Path(file_name).name
                image_path = images_dir / image_filename

                with zip_ref.open(file_name) as source, open(image_path, 'wb') as target:
                    target.write(source.read())

                image_paths.append(str(image_path))

    return image_paths