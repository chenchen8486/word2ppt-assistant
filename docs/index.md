# Word2PPT Assistant 架构全景

## 1. 核心理念：解耦与数据驱动
本项目摒弃了让 LLM 直接排版的错误方案。采用：**解析(MarkItDown) -> 结构化(LLM+JSON) -> 渲染(Marp CLI)** 的稳定流水线。

## 2. 数据目录流水线规范
程序运行时，必须依赖并维护以下目录结构（如不存在需自动创建）：
- `data/01_input_docs/`: 存放用户待转换的批量 `.docx` 文件。
- `data/02_temp_build/`: 存放所有中间产物。例如：`doc_name_raw.md` (解析出的纯文本), `doc_name_chunks.json` (分块数据), `doc_name_extracted.json` (大模型返回的结果), `doc_name_final.md` (Marp 语法文件)。这对于人类 Debug 至关重要。
- `data/03_output_pptx/`: 存放最终的 `.pptx` 结果。

## 3. 下一步行动
请读取并执行 `docs/phase1_data_and_parse.md`。