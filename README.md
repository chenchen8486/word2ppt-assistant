# Word2PPT Assistant

## 简介
**Word2PPT Assistant** 是一个基于 AI 的智能工具，旨在将 Word 格式的试卷自动转换为格式规范的 PowerPoint (PPT) 课件。它利用 Python 强大的文档处理能力结合 DeepSeek 大模型，实现题目的精准提取、题号对齐、答案解析关联以及图片的自动排版。

## 核心功能
*   **智能解析**：自动识别 Word 文档中的大题、小题、选项、答案和解析。
*   **结构对齐**：通过“题号对齐”算法，将散落在文档各处的答案和解析精准匹配到对应的题目上。
*   **AI 辅助**：利用 DeepSeek API 将题目文本拆分为“题干”和“选项”，优化 PPT 排版。
*   **图片支持**：自动提取 Word 中的图片（支持嵌入式和浮动图片），并将其关联到对应的题目页中。
*   **格式规范**：生成的 PPT 遵循“背景 -> 题目 -> 答案/解析”的教学演示逻辑，支持长文本自动分页。
*   **GUI 界面**：提供友好的图形用户界面，支持 API 配置、文件选择、日志查看等功能。
*   **配置记忆**：自动保存用户的 API Key、模型选择和路径设置，方便下次使用。

## 更新日志 (v1.1)
*   **优化排版**：移除所有红色字体，统一使用黑色和深灰色，提升专业度。
*   **字体规范**：固定了标题和正文的字号，避免随机变化。
*   **防溢出优化**：更严格的长文本分页策略（300字符/页），防止文字超出 PPT 边界。
*   **图片增强**：改进了图片提取逻辑，支持识别更多类型的嵌入图片（如第 23 题的复杂排版图片）。

## 安装指南

### 1. 环境要求
*   Python 3.8+
*   Windows 操作系统 (推荐)

### 2. 安装依赖
在项目根目录下运行以下命令安装所需的 Python 库：
```bash
pip install -r requirements.txt
```

*(如果尚未创建 requirements.txt，可以使用 `pip install python-docx python-pptx openai customtkinter json_repair`)*

## 使用说明

### 1. 启动程序
运行 `main.py` 启动图形界面：
```bash
python main.py
```

### 2. 配置设置
*   **API Key**: 输入您的 DeepSeek API Key。
*   **Base URL**: 默认为 `https://api.deepseek.com`，通常无需修改。
*   **AI 模型**: 选择 `DeepSeek-V3 (Chat)` 或 `DeepSeek-R1 (Reasoner)`。

### 3. 开始转换
1.  点击“选择试卷”按钮，选择需要转换的 Word 文档 (.docx)。
2.  点击“选择保存目录”，设置 PPT 的输出位置。
3.  点击“开始转换”，程序将自动解析文档并生成 PPT。
4.  转换完成后，您可以直接打开输出文件夹查看结果。

## 文档格式要求
为了获得最佳解析效果，Word 文档建议遵循以下结构：
*   **大题**：以中文数字开头，如“一、”、“二、”。
*   **小题**：以数字加点开头，如“1.”、“2.”。
*   **解析/答案**：建议包含“【答案】”和“【xx题详解】”标记。

## 目录结构
```
word2ppt-assistant/
├── core/               # 核心逻辑模块
│   ├── doc_loader.py   # (已废弃，由 standardizer 替代)
│   ├── standardizer.py # 文档结构化解析器
│   ├── llm_client.py   # LLM 接口客户端
│   └── ppt_generator.py# PPT 生成器
├── utils/              # 工具模块
│   ├── config_manager.py # 配置管理
│   └── logger.py       # 日志记录
├── logs/               # 日志输出目录
├── main.py             # 程序入口 (GUI)
├── requirements.txt    # 依赖列表
└── README.md           # 项目说明文档
```

## 许可证
MIT License
