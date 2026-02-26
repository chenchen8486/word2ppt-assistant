# Phase 4: 现代化 GUI 与批量调度

## 任务 1: 批量调度器
- 编写逻辑扫描 `data/01_input_docs/` 下所有的 `.docx`。
- 将 Phase 1 到 Phase 3 的流程串联为一个完整的 `process_single_file(filepath)` 工作流。

## 任务 2: CustomTkinter 主界面 (`main.py`)
- **UI 布局**:
  - 顶部：模型选择下拉框、API Key 确认状态。
  - 中部：两个大按钮：“打开输入文件夹 (Input)”、“打开输出文件夹 (Output)” (调用系统资源管理器 `os.startfile`)。
  - 底部：巨大的“开始批量转换”按钮、强制停止按钮。
  - 右侧：实时滚动的日志文本框。
- **线程安全**: 所有的批量处理流程必须在 `threading.Thread` 中执行，进度和日志通过线程安全队列或 `after` 方法更新到 UI，绝对禁止卡死主界面。