# 配置文件说明

## config/style_config.json

此文件用于配置PPTX生成的样式参数，包括：

- `font_family`: 默认文本字体（如："楷体", "微软雅黑", "宋体"）
- `number_font_family`: 数字/编号专用字体（如："黑体"）
- `font_size`: 默认字号（单位：pt）
- `line_spacing`: 行间距倍数（如：0.5, 1.0, 1.5, 2.0）
- `question_layout_idx`: 题目幻灯片布局索引
- `context_layout_idx`: 上下文幻灯片布局索引
- `context_placeholder_idx`: 上下文占位符索引
- `question_max_chars`: 题目幻灯片最大字符数
- `context_max_chars`: 上下文幻灯片最大字符数
- `answer_font_color`: 答案文字颜色 [R, G, B] 值（0-255）
- `analysis_font_color`: 解析文字颜色 [R, G, B] 值（0-255）
- `answer_font_bold`: 答案是否加粗 (true/false)
- `analysis_font_bold`: 解析是否加粗 (true/false)

## config.json (根目录 - 敏感配置)

这是一个非常重要的敏感配置文件，包含API密钥和模型设置。此文件对于应用程序运行至关重要，但由于包含敏感信息，**绝对不能提交到版本控制系统中**。

此文件包含：
- API密钥（DeepSeek、Qwen等）
- 模型端点和超时设置
- 应用程序默认配置
- 最近使用的路径信息

**重要安全提醒**：
1. 此文件已被添加到 .gitignore 中，不会被意外提交
2. 部署时请确保API密钥的安全存储
3. 定期轮换API密钥以保证安全
4. 不要在共享环境中暴露此文件

## 临时日志文件

某些情况下会在根目录生成临时日志文件，如：
- `crash_log.txt`: 程序崩溃时生成的错误日志
- `debug.log`: 调试日志

这些文件会被 .gitignore 忽略，一般在调试完成后可以安全删除。

## 日志文件

所有运行日志文件都存储在 `logs/` 目录中，包括：
- 程序运行日志
- 错误日志
- 调试日志

这些日志文件也会被 .gitignore 忽略，不被提交到版本控制系统中。