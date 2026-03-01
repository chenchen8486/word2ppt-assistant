# Phase 3: 模板驱动的 python-pptx 渲染引擎

## 任务 1: 解析母版架构
- **核心逻辑**: 完全使用 `python-pptx` 驱动，彻底废弃 Marp。
- **依赖模板**: 读取 `data/template.pptx` 作为渲染底座。
- **新架构**: Question 版式(Layout 2)采用"单占位符 + 段落富文本（Paragraph Rich Text）"的流式渲染方案。

## 任务 2: 编写渲染逻辑 (`core/pptx_generator.py`)
- **需求**: 读取 Phase 2 生成的 `_extracted.json`，按顺序遍历并生成 PPT。
- **渲染铁律**：
  1. **智能降噪**: 如果 `type == 'context'` 且文字不足 15 个字符（不含图片），直接跳过不渲染。
  2. **Context 渲染**: 遇到 `type == 'context'`，添加 `Layout 1`。将内容填入 `idx=13`。如果超过 450 字，按句号切分，并用 `Layout 1` 建立新页继续填充。
  3. **Question 渲染**: 遇到 `type == 'question'`，添加 `Layout 2`。使用"单占位符 + 段落富文本"的流式渲染：
     - 找到幻灯片中 `placeholder_format.type == 2` (Body Text) 的主文本框
     - 若找不到，则取可用占位符中体积/idx最大的
     - 清空默认文本后，流式写入：
       - 题干：写入首段落，18Pt，正常粗细
       - 答案：写入新段落 "\\n【答案】{answer}"，16Pt，加粗，红色 (RGBColor(220, 53, 69))
       - 解析：写入新段落 "\\n【解析】{analysis}"，16Pt，正常粗细，绿色 (RGBColor(40, 167, 69))

## 任务 3: 中间态落地
- 输出文件命名规范必须为：`data/03_output_pptx/{原文件名}.pptx`。

## 完成状态
- [x] 核心渲染逻辑实现
- [x] 智能降噪功能
- [x] 长文本熔断算法
- [x] 单占位符 + 段落富文本流式渲染方案
- [x] 使用 RGBColor 区分题目、答案和解析
- [x] Layout 1 & Layout 2 支持
- [x] MarpRenderer 已删除
- [x] 批量处理器已更新
- [x] 测试通过