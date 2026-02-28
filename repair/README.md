# Repair Scripts

本目录包含用于修复提取结果的脚本。这些脚本专注于通用性问题，而不是针对特定文档的修复。

## 保留的脚本及其功能

### 1. generic_repair.py
- 通用JSON数据修复脚本
- 修复最常见的extracted.json数据质量问题
- 处理缺失字段、非法字符等问题
- 按编号排序数据项

### 2. fix_extracted_structure.py
- 修复基本的结构问题
- 从错误消息中提取有效数据
- 确保所有项目都有正确格式

### 3. full_repair_extracted.py
- 完整修复提取的JSON文件
- 从原始混乱结构中提取所有有效数据
- 处理各种格式问题

### 4. fix_missing_parts.py
- 修复缺失字段
- 清理非法转义字符
- 确保所有必要字段存在

## 已移除的脚本

以下脚本因过度针对特定文档而被移除：
- `fix_section_three.py` - 针对特定部分的修复
- `fix_section_three_correct.py` - 针对特定部分的修复
- `fix_extracted_structure_v2.py` - 重复功能的修复脚本

## 使用方法

所有脚本都支持以下命令行用法：
```bash
python <script_name>.py <input_file> [output_file]
```

示例：
```bash
# 修复中文命名的文档
python generic_repair.py data/02_temp_build/我的文档_extracted.json

# 指定输出文件
python fix_extracted_structure.py data/02_temp_build/我的文档_extracted.json data/02_temp_build/我的文档_fixed.json
```

## 重要说明

- 所有脚本都专注于通用性修复，而非特定文档
- 在LLM处理阶段就应该生成高质量的JSON数据，修复脚本仅用于处理边缘情况
- 推荐优先改进LLM提示工程和数据提取质量，而不是依赖修复脚本