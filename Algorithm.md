# Word2PPT Assistant 算法手册 (Algorithm.md)

## 项目架构概览

```
输入: Word文档 (.docx)
     ↓
Phase 1: 文档解析 (Doc Loader)
     ↓
Phase 2: 内容分块 (Chunk Manager) - [重点改造点]
     ↓
Phase 3: LLM结构化提取 (LLM Client)
     ↓
Phase 4: PPTX生成 (PPTX Generator)
     ↓
输出: PowerPoint文档 (.pptx)
```

---

## Phase 1: 文档解析 (Doc Loader)

### 1.1 核心算法
- **输入**: `.docx` 文件
- **处理**: 使用 `markitdown` 库解析文档
- **输出**: `.raw.md` 文件

### 1.2 算法详情
```
1. 读取Word文档内容
2. 保留文本结构、图片、表格
3. 转换为Markdown格式
4. 输出到临时构建目录
```

### 1.3 涉及文件
- `utils/doc_loader.py`
- 输出路径: `data/02_temp_build/{filename}_raw.md`

### 1.4 可变参数
- 文档格式兼容性（不同版本Word）
- 图片/表格提取策略

---

## Phase 2: 内容分块 (Chunk Manager)

### 2.1 核心算法
- **输入**: Markdown格式文档
- **处理**: 基于规则的分块算法
- **输出**: `.chunks.json` 文件

### 2.2 当前分块规则
```
1. 大题识别规则 (Context):
   - 正则: r'^[一二三四五六七八九十\d]+[、.]'
   - 匹配: "一、二、三..." 或 "1、2、3..."

2. 小题识别规则 (Question):
   - 正则: r'^\d+[、.)）]'
   - 匹配: "1、2、3..." 或 "1) 2) 3)"

3. 选项识别规则:
   - 正则: r'^[ABCD][.、)]'
   - 匹配: "A、B、C、D" 或 "A. B. C. D."
```

### 2.3 分块逻辑
```
for each paragraph in markdown:
    if matches_context_pattern(paragraph):
        create_new_context_chunk()
    elif matches_question_pattern(paragraph):
        add_to_current_context(question_chunk)
    elif matches_option_pattern(paragraph):
        add_to_current_question(option_chunk)
```

### 2.4 涉及文件
- `core/chunk_manager.py`
- 输出路径: `data/02_temp_build/{filename}_chunks.json`

### 2.5 可变参数 - ⭐️【重点关注改造点】
- 正则表达式模式
- 分块长度限制
- 标题层级判断规则
- **针对化学试卷需调整**: 修改Context/Question识别规则

### 2.6 改造建议 (化学试卷场景)
```
化学试卷Context规则:
- r'^[一二三四五六七八九十\d]+[、.]' → r'^[化学反应\d+]:' 或 r'^实验[一二\d]+:'
- 识别实验描述、反应方程式等为Context

化学试卷Question规则:
- r'^\d+[、.)）]' → r'^[abcdefg][.、)]'
- 识别具体的化学问题为Question
```

---

## Phase 3: LLM结构化提取 (LLM Client)

### 3.1 核心算法
- **输入**: 分块后的JSON数据
- **处理**: LLM结构化解析
- **输出**: `.extracted.json` 文件

### 3.2 API交互流程
```
1. 遍历每个文档块
2. 构建结构化提取prompt
3. 调用LLM API (DeepSeek/OpenAI Compatible)
4. 解析返回的JSON结构
5. 验证和清洗数据
```

### 3.3 Prompt模板结构
```
System Prompt: "请将以下文档内容结构化为指定JSON格式..."
User Prompt:
{
  "instruction": "将以下文本转换为结构化数据",
  "content": "原始文本内容",
  "schema": "期望的JSON结构"
}
```

### 3.4 涉及文件
- `core/llm_client.py`
- 输出路径: `data/02_temp_build/{filename}_extracted.json`

### 3.5 可变参数
- LLM模型类型
- API端点配置
- 并发限制
- 重试次数
- 提示词模板

### 3.6 提示词优化 (化学试卷场景)
```
- 针对化学术语进行提示词微调
- 调整实体识别的prompt模板
- 添加化学式识别规则
```

---

## Phase 4: PPTX生成 (PPTX Generator)

### 4.1 核心算法
- **输入**: 结构化JSON数据
- **处理**: PowerPoint文档生成
- **输出**: `.pptx` 文件

### 4.2 渲染逻辑
```
1. 遍历JSON数据
2. 按类型渲染不同元素:
   - Context类型 → 标题幻灯片
   - Question类型 → 问题幻灯片
   - Options类型 → 选项幻灯片
3. 应用样式和布局
4. 生成PPTX文件
```

### 4.3 排版算法
- **字体**: 微软雅黑 14pt
- **权重计算**: 纯字符数 + (换行符数量 × 35)
- **翻页阈值**: Context 1200权重，Question 1000权重
- **贪心填充**: 当前页剩余空间优先利用

### 4.4 涉及文件
- `core/pptx_generator.py`
- 输出路径: `data/03_output_pptx/{filename}.pptx`

### 4.5 可变参数
- 字体设置
- 排版权重阈值
- 幻灯片布局
- 样式模板

### 4.6 化学公式渲染 (化学试卷场景)
- 需要特殊处理化学式格式
- 可能需要LaTeX渲染支持

---

## 针对化学试卷的改造路线

### A. 最优改造点: Phase 2 (Chunk Manager) - ⭐️⭐️⭐️⭐️⭐️
**推荐优先级最高**
- **原因**: 当前规则硬编码中文数字为Context，阿拉伯数字为Question
- **修改方法**:
  1. 更新正则表达式匹配规则
  2. 添加化学试卷专用的分块规则
  3. 识别"化学反应1、2、3"为Context
  4. 识别"a、b、c、d"为Question

### B. 次优改造点: Phase 3 (LLM Client) - ⭐️⭐️⭐️⭐️
- **原因**: 需要LLM更好地理解化学术语
- **修改方法**:
  1. 更新提示词模板，加入化学术语识别
  2. 添加化学式、分子式识别规则
  3. 优化实体抽取的prompt

### C. 辅助改造点: Phase 4 (PPTX Generator) - ⭐️⭐️⭐️
- **原因**: 化学式可能需要特殊的渲染方式
- **修改方法**:
  1. 添加化学式渲染支持
  2. 优化排版算法处理化学式

### D. 边缘改造点: Phase 1 (Doc Loader) - ⭐️⭐️
- **原因**: 一般不需要特殊处理
- **修改方法**: 仅在文档格式差异很大时考虑

---

## 关键配置文件

### config.json - 全局配置
```
{
  "models": {  // LLM配置
    "deepseek": {...},
    "qwen": {...}
  },
  "settings": {  // 全局设置
    "default_model": "...",
    "timeout": 300
  },
  "last_used_paths": {  // 历史路径记忆
    "input_folder": "...",
    "output_folder": "..."
  }
}
```

### 配置可变参数
- API密钥
- 模型选择
- 超时设置
- 并发限制

---

## 文件流路径

### 输入目录
- `data/01_input_docs/` - Word文档输入

### 临时构建目录
- `data/02_temp_build/` - 中间处理文件
  - `{filename}_raw.md` - Phase 1输出
  - `{filename}_chunks.json` - Phase 2输出
  - `{filename}_extracted.json` - Phase 3输出

### 输出目录
- `data/03_output_pptx/` - PPTX输出

---

## 改造影响评估

### Phase 2 修改影响
- **影响范围**: 核心分块逻辑
- **风险等级**: 中等
- **测试要点**: 确保其他试卷格式仍可正常使用
- **推荐方案**: 创建针对化学试卷的专用分块规则

### Phase 3 修改影响
- **影响范围**: LLM提示词和输出格式
- **风险等级**: 较低
- **测试要点**: 确保JSON结构符合下游要求

### Phase 4 修改影响
- **影响范围**: PPT渲染效果
- **风险等级**: 低
- **测试要点**: 化学式显示效果

---

## 化学试卷专项适配建议

### 推荐改造路径
1. **第一步**: 扩展Phase 2的分块规则识别化学试卷格式
2. **第二步**: 微调Phase 3的提示词以更好地理解化学内容
3. **第三步**: 优化Phase 4的渲染以处理化学式显示

### 具体实施要点
- 保留原有通用规则兼容性
- 添加化学试卷专用规则分支
- 实现格式自动检测机制
- 建立化学术语词典

---