# Word2PPT 样式配置指南

## 配置文件路径
配置文件位于 `config/style_config.json`

## 配置选项说明

### 字体设置
- `font_family`: 默认字体，例如 "楷体", "微软雅黑", "宋体" 等
- `number_font_family`: 数字/编号专用字体，例如 "黑体"
- `font_size`: 默认字号，单位 pt

### 行间距设置
- `line_spacing`: 行间距倍数，例如 0.5, 1.0, 1.5, 2.0

### 布局设置
- `question_layout_idx`: 题目幻灯片布局索引
- `context_layout_idx`: 上下文幻灯片布局索引
- `context_placeholder_idx`: 上下文占位符索引
- `question_max_chars`: 题目幻灯片最大字符数
- `context_max_chars`: 上下文幻灯片最大字符数

### 颜色设置
- `answer_font_color`: 答案颜色，格式 [R, G, B]，范围 0-255
- `analysis_font_color`: 解析颜色，格式 [R, G, B]，范围 0-255

### 样式设置
- `answer_font_bold`: 答案是否加粗 (true/false)
- `analysis_font_bold`: 解析是否加粗 (true/false)

## 示例配置
```json
{
    "font_family": "楷体",
    "font_size": 14,
    "line_spacing": 1.5,
    "question_layout_idx": 2,
    "context_layout_idx": 1,
    "context_placeholder_idx": 0,
    "question_max_chars": 1000,
    "context_max_chars": 1200,
    "number_font_family": "黑体",
    "answer_font_color": [220, 53, 69],
    "answer_font_bold": true,
    "analysis_font_color": [40, 167, 69],
    "analysis_font_bold": false
}
```

## 使用说明
1. 修改配置文件后，重启应用程序使配置生效
2. 如需恢复默认设置，删除配置文件，程序会自动生成默认配置
3. 配置仅影响新生成的PPTX文件