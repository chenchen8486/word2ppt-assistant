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

## config.json (根目录)

这是一个敏感配置文件，包含API密钥和模型设置。由于包含敏感信息，此文件不应被提交到版本控制系统中。请确保：

1. 不要将此文件提交到公共代码仓库
2. 在部署时，确保API密钥的安全存储
3. 根据需要调整模型端点和超时设置

## 日志文件

所有日志文件都存储在 `logs/` 目录中，包括：
- 程序运行日志
- 错误日志
- 调试日志

这些日志文件也会被 .gitignore 忽略，不被提交到版本控制系统中。