# Word2PPT Assistant 架构全景

## 1. 核心理念：解耦与数据驱动
本项目摒弃了让 LLM 直接排版的错误方案。采用：**解析(MarkItDown) -> 结构化(LLM+JSON) -> 渲染(python-pptx 模板驱动)** 的稳定流水线。

## 2. 数据目录流水线规范
程序运行时，必须依赖并维护以下目录结构（如不存在需自动创建）：
- `data/01_input_docs/`: 存放用户待转换的批量 `.docx` 文件。
- data/02_temp_build/: 存放所有中间产物。例如：doc_name_raw.md (解析出的纯文本), doc_name_chunks.json (分块数据), doc_name_extracted.json (大模型返回的结果)。这对于人类 Debug 至关重要。
- `data/03_output_pptx/`: 存放最终的 `.pptx` 结果。

## 3. 开发阶段
- Phase 1: 数据流搭建与文档解析
- Phase 2: 智能分块与 Few-Shot 提取
- Phase 3: 模板驱动的 python-pptx 渲染引擎
- Phase 4: 端到端集成测试
- Phase 5: 数据完整性验证与修复机制

## 4. 下一步行动
请根据需要读取相应阶段的文档。

## 最新进展
- 2026-02-28: 完成了Phase 5的数据完整性验证与修复机制，解决了test_extracted.json中残留的错误数据问题。
- 2026-02-28: 修复了core/llm_client.py中_clean_response_content函数的实现，改用正则表达式直接提取JSON内容，提升了对LLM输出格式变化的鲁棒性。
- 2026-02-28: 修复了core/llm_client.py中的并发超时问题，通过降低并发数(TCPConnector limit: 10->3)和增加超时时间(60s->300s)解决了API限流和长文本处理问题。
- 2026-02-28: 改进了错误处理策略，不再静默丢弃错误数据，改为生成显眼的错误条目以暴露问题，提高了系统的透明度和可调试性。