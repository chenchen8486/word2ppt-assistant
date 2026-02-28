# Word2PPT Assistant 项目结构

## 概述
本项目旨在将Word文档智能转换为PPT演示文稿。项目结构经过整理，将不同类型的脚本按功能分类存放。

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
├── scripts/                  # 通用脚本目录
│   ├── add_missing_questions.py     # 添加缺失问题
│   ├── advanced_rebuild.py          # 高级重建脚本
│   ├── setup_config.py             # 配置设置脚本
│   ├── verify_and_fix_questions.py  # 验证和修复问题脚本
│   └── verify_rules.py             # 验证规则脚本
├── build/                    # 构建相关脚本目录
│   ├── build_from_chunks.py         # 从分块构建
│   ├── post_process_validate.py     # 后处理验证
│   ├── precise_build.py             # 精确构建
│   ├── precise_rebuild.py           # 精确重建
│   ├── complete_rebuild.py          # 完整重建
│   ├── rebuild_extracted.py         # 重建提取结果
│   ├── recreate_extracted.py        # 重新创建提取结果
│   ├── recreate_extracted_clean.py  # 重新创建清洁版提取结果
│   ├── restructure_extracted.py     # 重构提取结果
│   └── reorder_extracted.py         # 重新排序提取结果
├── validation/               # 验证脚本目录
│   ├── validate_data.py             # 验证数据完整性
│   ├── validate_merged.py           # 验证合并结果
│   ├── validate_structure.py        # 验证结构
│   ├── validate_repair.py           # 验证修复
│   └── merge_json.py               # JSON合并
├── repair/                   # 修复脚本目录
│   ├── fix_extracted_structure.py        # 修复提取结构
│   ├── fix_extracted_structure_v2.py     # 修复提取结构v2
│   ├── full_repair_extracted.py          # 完整修复提取结果
│   ├── fix_missing_parts.py              # 修复缺失部分
│   ├── fix_section_three.py              # 修复第三部分
│   └── fix_section_three_correct.py      # 修复第三部分修正版
├── test/                     # 测试脚本目录
│   ├── unit_tests/           # 单元测试
│   │   ├── __init__.py
│   │   ├── test_phase1.py   # 第一阶段单元测试
│   │   ├── test_phase2.py   # 第二阶段单元测试
│   │   ├── test_phase3.py   # 第三阶段单元测试
│   │   └── test_phase4.py   # 第四阶段单元测试
│   ├── integration_tests/    # 集成测试和功能验证脚本
│   │   ├── __init__.py
│   │   ├── run_e2e_test.py         # 端到端测试
│   │   ├── run_test_pptx.py        # PPTX测试
│   │   ├── run_phase3_validation.py # Phase3验证
│   │   └── comprehensive_check.py   # 综合检查
│   └── run_tests.py          # 统一测试入口脚本
├── tests/                    # 单元测试目录
│   ├── __init__.py
│   ├── test_phase1.py         # 第一阶段测试
│   ├── test_phase2.py         # 第二阶段测试
│   ├── test_phase3.py         # 第三阶段测试
│   └── test_phase4.py         # 第四阶段测试
├── user_templates/           # 用户模板目录
│   ├── 01_raw_input.md       # 原始输入模板
│   └── 02_target_output.json # 目标输出模板
├── utils/                    # 工具模块
│   ├── __init__.py
│   ├── config_manager.py      # 配置管理器
│   ├── dependency_manager.py  # 依赖管理器
│   ├── doc_loader.py          # 文档加载器
│   ├── file_helper.py         # 文件辅助工具
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

### 脚本说明
- `scripts/` - 包含各种实用工具脚本
- `build/` - 包含构建相关的脚本
- `validation/` - 包含数据验证脚本
- `repair/` - 包含数据修复脚本
- `test/` - 包含测试脚本

### 数据流水线
项目遵循严格的三阶段数据流水线：
1. `data/01_input_docs/` - 输入的Word文档
2. `data/02_temp_build/` - 中间处理结果
3. `data/03_output_pptx/` - 最终PPTX输出

## 开发规范

遵循 `AGENTS.md` 中定义的开发原则，包括：
- 严格的数据流水线管理
- 黄金样本保护
- 测试驱动开发
- 渐进式执行
