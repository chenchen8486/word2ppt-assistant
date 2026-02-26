# Phase 1: 数据流搭建与文档解析

## 任务 1: 目录初始化与工具类 (`utils/file_helper.py`)
- 编写初始化函数，在启动时自动检查并创建 `data/01_input_docs`, `data/02_temp_build`, `data/03_output_pptx`, `user_templates` 以及 `bin/` 目录。

## 任务 2: 现代文档解析器 (`utils/doc_loader.py`)
- **需求**: 封装微软 `markitdown` 库。
- **逻辑**: 接收一个 `.docx` 路径。调用 `MarkItDown().convert()` 提取 Markdown。
- **中间态落地**: 将提取出的原始 Markdown 文本，以 `utf-8-sig` 编码保存到 `data/02_temp_build/{原文件名}_raw.md` 中。
- **图片处理**: 使用 `zipfile` 解压 `.docx`，将其 `word/media/` 下的图片提取到 `data/02_temp_build/{原文件名}_images/` 目录下。

## 验证标准
编写测试用例，放入一个测试 docx 到输入目录，验证能否正确解析出纯文本并保存到 `temp_build` 目录中。测试通过后 Git Commit。