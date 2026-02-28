# Phase 3: 模板驱动的 python-pptx 渲染引擎

## 任务 1: 解析母版架构
- **核心逻辑**: 彻底废弃 Marp，改用 `python-pptx` 库。
- **依赖模板**: 必须读取事先做好的 `data/template.pptx` 作为渲染底座。
- 已知的占位符映射关系：
  - `Layout 1` (用于大题背景): 文本占位符 `idx=13`
  - `Layout 2` (用于具体题目): 题干 `idx=13`，答案 `idx=14`，解析 `idx=15`

## 任务 2: 编写渲染逻辑 (`core/pptx_generator.py`)
- **需求**: 读取 Phase 2 生成的 `_extracted.json`，按顺序遍历并生成 PPT。
- **渲染铁律**：
  1. **智能降噪**: 如果 `type == 'context'` 且文字不足 15 个字符（不含图片），直接跳过不渲染。
  2. **Context 渲染**: 遇到 `type == 'context'`，添加 `Layout 1`。将内容填入 `idx=13`。如果超过 450 字，按句号切分，并用 `Layout 1` 建立新页继续填充。
  3. **Question 渲染**: 遇到 `type == 'question'`，添加 `Layout 2`。将内容分别填入对应的 3 个 idx。如果答案或解析极其冗长（超 400 字），按句号切分，并在下一张 `Layout 2` 中继续填充对应位置。

## 任务 3: 中间态落地
- 输出文件命名规范必须为：`data/02_temp_build/04_{原文件名}_final.pptx`。

## 完成状态
- [x] 核心渲染逻辑实现
- [x] 智能降噪功能
- [x] 长文本熔断算法（按450字切分context，按400字切分answer/analysis）
- [x] Layout 1 & Layout 2 支持
- [x] 测试通过