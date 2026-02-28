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
- `comprehensive_check.py`: 数据完整性校验
- `full_repair_extracted.py`: 数据修复工具

## 使用方法

### 1. 单文件处理
```bash
python test/run_e2e_test.py  # 端到端测试
```

### 2. 生成PPTX
```bash
python test/run_test_pptx.py  # 直接生成PPTX文件
```

### 3. 数据校验
```bash
python test/comprehensive_check.py  # 验证数据完整性
```

### 4. 数据修复
```bash
# 修复损坏的extracted.json文件（支持任意文档名称，包括中文）
python repair/generic_repair.py data/02_temp_build/your_document_extracted.json

# 或指定输出文件
python repair/fix_extracted_structure.py data/02_temp_build/我的文档_extracted.json data/02_temp_build/我的文档_fixed.json
```

## 修复脚本改进

修复脚本现在专注于通用性问题，避免过度针对性：
- 移除了针对特定文档部分的修复脚本
- 保留了通用性修复功能（如`generic_repair.py`）
- 优化了LLM客户端，提高首次提取的准确性
- 减少了对后续修复脚本的依赖

### 修复脚本列表
- `repair/generic_repair.py`: 通用数据修复
- `repair/fix_extracted_structure.py`: 基本结构修复
- `repair/full_repair_extracted.py`: 完整修复提取结果
- `repair/fix_missing_parts.py`: 修复缺失部分

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