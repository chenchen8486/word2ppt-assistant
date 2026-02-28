# Word转PPT助手

一个自动化工具，可将Word文档转换为PPT演示文稿，特别适用于处理包含文本、表格和图像的结构化文档（如考试题、练习题等）。

## 功能特性

- **智能解析**: 从Word文档中提取文本内容，保持结构完整性
- **内容分块**: 将长文档分割为合适的处理单元
- **AI处理**: 使用LLM对内容进行结构化提取和分析
- **多格式输出**: 支持Markdown (Marp) 和 PowerPoint (PPTX) 格式
- **数据完整性**: 包含错误处理和数据修复机制
- **验证校验**: 全面的数据完整性验证

## 工作流程

1. **文档解析**: 从 `.docx` 文件中提取内容，保存为 `.raw.md`
2. **内容分块**: 将长文档分割为多个块，保存为 `.chunks.json`
3. **AI处理**: 使用大语言模型结构化提取内容，保存为 `.extracted.json`
4. **渲染**: 将结构化数据渲染为 Marp 格式的 Markdown 文件
5. **转换**: 将 Markdown 转换为 PowerPoint 演示文稿

## 目录结构

```
data/
├── 01_input_docs/          # 输入的Word文档
├── 02_temp_build/          # 临时构建文件
│   ├── *.raw.md           # 原始提取内容
│   ├── *.chunks.json      # 内容分块
│   ├── *.extracted.json   # 结构化提取结果
│   ├── *.final.md         # 最终Markdown文件
│   └── *.images/          # 图像资源
└── 03_output_pptx/         # 最终PPTX输出
```

## 主要组件

- `core/batch_processor.py`: 批量处理引擎
- `core/llm_client.py`: LLM交互客户端
- `core/marp_renderer.py`: Marp渲染器
- `core/pptx_generator.py`: PPTX生成器
- `utils/doc_loader.py`: 文档加载工具
- `utils/data_repair.py`: 通用数据修复工具
- `utils/data_validator.py`: 数据验证工具
- `utils/build_tools.py`: 构建工具
- `tests/integration_tests/integration_suite.py`: 集成测试套件

## 架构优化

在最近的重构中，我们精简了项目结构：
- 消除了过度工程化的目录结构
- 将repair/, validation/, build/功能整合到utils/模块
- 将零散的测试脚本整合到统一的测试套件中
- 保持了核心业务功能不变，仅优化了组织结构
- 提高了代码的可维护性和可读性

## 使用方法

### 1. 单文件处理
```bash
python tests/integration_tests/integration_suite.py e2e  # 端到端测试
```

### 2. 生成PPTX
```bash
python tests/integration_tests/integration_suite.py pptx  # 直接生成PPTX文件
```

### 3. 数据校验
```bash
python tests/integration_tests/integration_suite.py comprehensive  # 验证数据完整性
```

### 4. 渲染验证
```bash
python tests/integration_tests/integration_suite.py phase3  # Phase3验证
```

## 核心功能说明

### 数据完整性验证与修复机制

1. **JSON数据序列完整性验证** - 检测题目编号是否连续
2. **自动修复缺失题目** - 从备份源获取缺失内容
3. **数据顺序重组** - 按逻辑关系重新排列context-question对
4. **错误数据处理与恢复** - 从损坏JSON中提取有效数据
5. **综合数据校验** - 全面验证数据完整性

### 验证规则

- 所有项目包含必要字段（type, number, content）
- Question项目包含answer和analysis字段
- Context和Question按逻辑顺序排列
- 题目编号连续完整（1-24题及子题）
- 无错误条目或损坏数据

## 支持的文档类型

特别适合处理包含以下结构的文档：
- 上下文段落（如"一、二、三..."）
- 选择题（如"1、2、3..."）
- 填空题、问答题
- 包含答案和解析的题目

## 技术栈

- Python 3.x
- python-docx (文档解析)
- OpenAI API / DeepSeek或其他LLM接口
- python-pptx (PPT生成)
- markdown-it-py (Markdown处理)
- Marp (用于PPTX转换)

## 注意事项

- 确保API密钥配置正确
- 文档内容格式应相对规整以获得最佳效果
- 如遇处理错误，可使用数据修复工具进行恢复
- 中间文件会自动管理，但可以手动清理
- 为增强LLM响应的健壮性，系统会在发送请求时要求LLM遵守严格的JSON输出格式，并在接收响应时对非法转义字符进行清理

## 开发阶段

- Phase 1: 文档解析与内容提取
- Phase 2: 内容分块与预处理
- Phase 3: AI结构化提取与渲染
- Phase 4: Marp渲染与PPTX转换
- Phase 5: 数据完整性验证与修复