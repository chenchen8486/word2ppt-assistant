# Phase 3: 基于 JSON 的严格 Marp 渲染引擎

## 任务 1: 定义 Marp 样式底座 (Theme)
- **需求**: 在生成的 Markdown 头部，必须注入 Marp 的 Front-matter 和全局样式（使用 `<style>` 标签或外部 css），以确保字号统一和结构紧凑。
- **排版铁律**:
  1. 大题背景字号较小 (如 `20px` 或 `1.2rem`)。
  2. 小题（题干、答案、解析）字号稍大 (如 `28px` 或 `1.5rem`)。
  3. 强调颜色：【答案】和【解析】等关键字可以使用加粗和特定颜色区分。

## 任务 2: Python 智能渲染逻辑 (`core/marp_renderer.py`)
- **需求**: 读取 `_extracted.json`，将其严格按顺序渲染为 Marp MD 文件。
- **绝对渲染顺序与分页规则** (必须在代码逻辑中严格实现)：
  - **遍历 JSON 数组**：必须严格按先后顺序读取。
  - **处理 context (大题背景文字)**：
    - 渲染格式：包裹在较小字号的 HTML 标签中，如 `<div style="font-size: 20px; line-height: 1.5;">{text}</div>`。
    - **防溢出分页算法**：代码中必须实现一个字符统计检测。如果单个 `context` 文本超过预设的安全字数（例如 400 字），Python 必须将其分割成两半，并在中间插入 `---` 强制换页，绝对不能让文字溢出 PPT 边界。
  - **处理 question (具体小题)**：
    - 每道小题最多只占用 1-2 页，确保结构紧凑。
    - **第一页 (题干)**：使用稍大字号 `## {number}. {content}`。
    - **第二页 (完整解析)**：插入 `---` 换页。展示题干 +【答案】{answer} +【解析】{analysis}。同样需要字数防溢出检测，如果解析过长，通过 `---` 再分一页。
  - **处理图片**：如果文本中包含提取出的图片名（如 `image1.png`），自动替换为 Marp 图片防溢出语法 `![bg right:40% fit](图片路径)` 或 `![width:800px](图片路径)`。

## 任务 3: 中间态落地与 CLI 调度
- 将最终生成的完整 Markdown 字符串，保存为 `data/02_temp_build/{原文件名}_final.md` (强制使用 `utf-8-sig`)。
- 调用 `subprocess.run`，使用 `bin/marp.exe` 将 `_final.md` 编译为 `.pptx`。
- 输出路径设定为 `data/03_output_pptx/{原文件名}.pptx`。

## 验证标准
1. 编写测试：输入一个包含 800 字超长 context 和 3 道 question 的 Mock JSON。
2. 验证 `marp_renderer.py` 生成的 MD 文件是否正确插入了 `<style>`，是否在 800 字的长文本中间正确插入了 `---` 进行了防溢出分页。
3. 验证通过后，Git Commit。