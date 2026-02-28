# Word2PPT Assistant 架构全景

## 1. 核心理念：解耦与数据驱动
本项目摒弃了让 LLM 直接排版的错误方案。采用：**解析(MarkItDown) -> 结构化(LLM+JSON) -> 渲染(python-pptx 模板驱动)** 的稳定流水线。

## 2. 数据目录流水线规范
程序运行时，必须依赖并维护以下目录结构（如不存在需自动创建）：
- `data/01_input_docs/`: 存放用户待转换的批量 `.docx` 文件。
- `data/02_temp_build/`: 存放所有中间产物。例如：doc_name.raw.md (解析出的纯文本), doc_name_chunks.json (分块数据), doc_name_extracted.json (大模型返回的结果)。这对于人类 Debug 至关重要。
  - `data/02_temp_build/archive/`: 存放历史遗留的或非标准的数据文件归档，常规运行不会向此目录写入新数据。
- `data/03_output_pptx/`: 存放最终的 `.pptx` 结果。

## 3. 项目结构
现在项目结构已规范化，遵循极简工程原则，脚本按功能分类存放：
- `main.py`: 主应用程序入口 (GUI界面)
- `config.json`: 配置文件
- `requirements.txt`: 依赖包列表
- `README.md`: 项目说明
- `PROJECT_STRUCTURE.md`: 项目结构说明
- `AGENTS.md`: 智能体行为准则
- `PROJECT_SUMMARY.md`: 项目摘要
- `bin/`: 可执行文件目录
- `core/`: 核心模块（批处理器、LLM客户端、渲染器等）
- `utils/`: 工具模块（配置管理、依赖管理、数据修复、数据验证、构建工具等）
- `tests/`: 统一测试目录
  - `unit_tests/`: 单元测试（按开发阶段划分）
  - `integration_tests/`: 集成测试和功能验证脚本
  - `run_tests.py`: 统一测试入口脚本
- `docs/`: 项目文档
- `data/`: 数据流水线目录
  - `01_input_docs/`: 输入文档
  - `02_temp_build/`: 临时构建文件
  - `03_output_pptx/`: 输出PPTX
- `user_templates/`: 用户模板目录

## 4. 开发阶段
- Phase 1: 数据流搭建与文档解析
- Phase 2: 智能分块与 Few-Shot 提取
- Phase 3: 模板驱动的 python-pptx 渲染引擎
- Phase 4: 端到端集成测试
- Phase 5: 数据完整性验证与修复机制

## 5. 数据管理规范
- 标准流水线产生的中间文件始终保存在 `data/02_temp_build/` 目录下
- 每个文档处理后会生成四个标准文件：`.raw.md`, `.chunks.json`, `.extracted.json`, `.final.md`
- 临时或历史遗留的数据文件会被归档到 `data/02_temp_build/archive/` 目录中
- 不会将中间结果自动保存到归档目录，归档目录仅用于手动整理

## 6. 改进的修复策略
- 修复脚本现在专注于通用性问题，避免过度针对性
- 移除了针对特定文档部分的修复脚本
- 优化LLM客户端，提高首次提取的准确性
- 保留了`generic_repair.py`等通用修复脚本用于处理边缘情况

## 7. 下一步行动
请根据需要读取相应阶段的文档。

## 最新进展
- 2026-02-28: 项目结构已完成极简化重构，消除了过度工程化的目录结构，将repair/, validation/, build/等功能整合到utils/模块，零散的测试脚本整合到统一的测试套件中，大幅提升了代码的可维护性和可读性。
- 2026-02-28: 创建了 utils/data_repair.py - 整合了原repair目录的通用修复功能
- 2026-02-28: 创建了 utils/data_validator.py - 整合了原validation目录的验证功能
- 2026-02-28: 创建了 utils/build_tools.py - 整合了原build目录的构建功能
- 2026-02-28: 创建了 tests/integration_tests/integration_suite.py - 统一的测试套件，整合了原有的零散测试功能
- 2026-02-28: 更新了PROJECT_STRUCTURE.md和README.md文档，反映了新的极简架构
- 2026-02-28: 项目遵循了"消除过度工程化，保持核心功能不变"的设计哲学，实现了更简洁合理的组织结构