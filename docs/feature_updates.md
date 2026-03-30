# Word2PPT 助手功能更新说明

## 新增功能：样式配置

### 配置功能
现在 Word2PPT 助手支持自定义样式配置，您可以通过修改配置文件来自定义生成的 PPTX 文档样式。

### 配置选项
1. **字体设置**：
   - `font_family`: 文本字体（如：楷体、微软雅黑等）
   - `number_font_family`: 题号/数字专用字体（如：黑体）

2. **行间距设置**：
   - `line_spacing`: 行间距倍数（如：0.5、1.0、1.5、2.0）

3. **布局设置**：
   - `question_layout_idx`: 题目幻灯片布局索引
   - `context_layout_idx`: 上下文幻灯片布局索引
   - `context_placeholder_idx`: 上下文占位符索引

4. **色彩设置**：
   - `answer_font_color`: 答案文字颜色
   - `analysis_font_color`: 解析文字颜色

5. **样式设置**：
   - `answer_font_bold`: 答案是否加粗
   - `analysis_font_bold`: 解析是否加粗

### 配置文件位置
- 配置文件路径：`config/style_config.json`
- 如果配置文件不存在，程序会自动使用默认设置

### 使用方法
1. 修改 `config/style_config.json` 文件中的相应参数
2. 重启应用程序使配置生效
3. 新生成的 PPTX 文件将使用您自定义的样式

### 默认配置
默认配置保持原有的样式设定，以确保现有用户的使用体验不受影响。

### 注意事项
- 配置仅影响新生成的PPTX文件
- 删除配置文件将恢复默认设置
- 配置参数根据您的系统和字体库情况调整