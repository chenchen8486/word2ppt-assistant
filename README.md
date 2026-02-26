# Word2PPT Assistant

一个支持批量处理、基于 LLM 将 Word 试卷结构化并转换为高质量 PPTX 的本地 GUI 应用。

## 目录结构说明

### `data/01_input_docs/`
- 存放用户待转换的批量 `.docx` 文件

### `data/02_temp_build/`
- 存放所有中间产物，主要包括：
  - `{filename}_raw.md` - 解析出的原始 Markdown 内容
  - `{filename}_chunks.json` - 分块后的结构化文档（重要的中间结果）
  - `{filename}_extracted.json` - LLM 提取的结构化数据（重要的中间结果）
  - `{filename}_final.md` - 最终的 Marp 语法文件
  - `{filename}_images/` - 从文档中提取的图片

### `data/03_output_pptx/`
- 存放最终生成的 `.pptx` 结果

## 使用说明

1. 将需要转换的 Word 文档放到 `data/01_input_docs/` 目录
2. 运行 `python main.py` 启动 GUI
3. 在界面上选择模型并确保 API 密钥已配置
4. 点击"开始批量转换"按钮
5. 转换完成后的 PPTX 文件将输出到 `data/03_output_pptx/` 目录

## 配置

首次运行前，请编辑 `config.json` 文件，填入您的 LLM API 密钥。

支持的模型：
- DeepSeek
- Qwen

## 依赖

- customtkinter
- markitdown
- aiohttp
- pytest (测试用)

## 工作流程

1. **解析** - 使用 markitdown 库解析 Word 文档
2. **分块** - 按题目将长文档切分成小块
3. **提取** - 使用 LLM 提取结构化数据 (type, number, content, answer, analysis)
4. **渲染** - 转换为 Marp 格式并生成 PPTX