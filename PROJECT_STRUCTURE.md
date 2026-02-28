# Word2PPT Assistant 项目结构

## 概述
本项目旨在将Word文档智能转换为PPT演示文稿。经过重构，现在采用更简洁的结构，将相关功能整合到核心模块中。

## 目录结构

```
word2ppt-assistant/
├── main.py                    # 主应用程序入口 (GUI界面)
├── config.json               # 配置文件
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目说明
├── PROJECT_STRUCTURE.md      # 本文件 - 项目结构说明
├── AGENTS.md                 # 智能体行为准则
├── PROJECT_SUMMARY.md        # 项目摘要
├── bin/                      # 可执行文件目录
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── batch_processor.py    # 批量处理引擎
│   ├── chunk_manager.py      # 内容分块管理器
│   ├── llm_client.py         # LLM客户端
│   ├── marp_renderer.py      # Marp渲染器
│   ├── pptx_generator.py     # PPTX生成器
│   └── __pycache__/          # Python缓存目录
├── data/                     # 数据流水线目录
│   ├── 01_input_docs/        # 输入的Word文档
│   ├── 02_temp_build/        # 临时构建文件
│   └── 03_output_pptx/       # 输出的PPTX文件
├── docs/                     # 文档目录
│   ├── index.md              # 项目架构全景
│   ├── phase1_data_and_parse.md  # 第一阶段文档
│   ├── phase2_data_and_parse.md  # 第二阶段文档
│   ├── phase3_data_and_parse.md  # 第三阶段文档
│   ├── phase4_data_and_parse.md  # 第四阶段文档
│   ├── phase5_data_validation.md # 第五阶段文档
│   └── concurrent_timeout_fix.md # 并发超时修复说明
├── tests/                    # 测试脚本目录
│   ├── unit_tests/           # 单元测试
│   │   ├── __init__.py
│   │   ├── test_phase1.py   # 第一阶段单元测试
│   │   ├── test_phase2.py   # 第二阶段单元测试
│   │   ├── test_phase3.py   # 第三阶段单元测试
│   │   └── test_phase4.py   # 第四阶段单元测试
│   ├── integration_tests/    # 集成测试和功能验证脚本
│   │   ├── __init__.py
│   │   └── integration_suite.py   # 集成测试套件
│   └── run_tests.py          # 统一测试入口脚本
├── user_templates/           # 用户模板目录
│   ├── 01_raw_input.md       # 原始输入模板
│   └── 02_target_output.json # 目标输出模板
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── config_manager.py      # 配置管理器
│   ├── dependency_manager.py  # 依赖管理器
│   ├── doc_loader.py          # 文档加载器
│   ├── file_helper.py         # 文件辅助工具
│   ├── data_repair.py         # 数据修复工具（整合原repair功能）
│   ├── data_validator.py      # 数据验证工具（整合原validation功能）
│   ├── build_tools.py         # 构建工具（整合原build功能）
│   └── __pycache__/          # Python缓存目录
├── .claude/                  # Claude Code配置
├── .git/                     # Git仓库信息
├── .vscode/                  # VS Code配置
├── .pytest_cache/            # PyTest缓存
└── memory/                   # 记忆目录
```

## 使用说明

### 核心应用
- `main.py` - 启动GUI应用程序

### 核心模块 (core/)
- `batch_processor.py`: 批量处理引擎，协调整个工作流程
- `chunk_manager.py`: 文档内容分块管理
- `llm_client.py`: 与大语言模型交互，提取结构化数据
- `marp_renderer.py`: Marp渲染引擎，将JSON数据转换为Markdown
- `pptx_generator.py`: 将Markdown转换为PPTX格式

### 工具模块 (utils/)
- `config_manager.py`: 管理应用配置
- `dependency_manager.py`: 依赖管理
- `doc_loader.py`: 文档加载和解析
- `file_helper.py`: 文件操作辅助
- `data_repair.py`: 整合了原repair目录的功能，提供通用数据修复
- `data_validator.py`: 整合了原validation目录的功能，提供数据验证
- `build_tools.py`: 整合了原build目录的功能，提供构建相关工具

### 测试模块 (tests/)
- `unit_tests/`: 按开发阶段划分的单元测试
- `integration_tests/integration_suite.py`: 统一的集成测试套件，整合了原来分散的测试功能

### 数据流水线
项目遵循严格的三阶段数据流水线：
1. `data/01_input_docs/` - 输入的Word文档
2. `data/02_temp_build/` - 中间处理结果
3. `data/03_output_pptx/` - 最终PPTX输出

## 架构优化说明

在本次重构中：
1. 消除了过度工程化的目录结构
2. 将repair/, validation/, build/三个冗余目录的功能整合到utils/中
3. 将零散的测试脚本整合到统一的测试套件中
4. 保持了核心业务功能不变，仅优化了组织结构
5. 提高了代码的可维护性和可读性
