# Phase 2: 智能分块与 Few-Shot 提取

## 任务 1: 大题分块管理器 (`core/chunk_manager.py`)
- **需求**: 避免 LLM 漏题，需将几万字按大题切分。
- **逻辑**: 读取 `temp_build` 里的 `_raw.md`，利用正则匹配中文数字题号（如 `一、`, `二、`）或 `第X卷` 进行分块。
- **中间态落地**: 将切分好的列表保存为 `data/02_temp_build/{原文件名}_chunks.json`。

## 任务 2: 动态 Few-Shot 客户端 (`core/llm_client.py`)
- **密钥读取**: 从根目录 `API_KEY.txt` 中安全读取 DeepSeek/Qwen 密钥。
- **Few-Shot 植入**: 读取 `user_templates/01_raw_input.md` 和 `02_target_output.json` 作为 System Prompt 的示例。
- **并发提取**: 遍历 Chunk 列表，并发请求 LLM，要求 LLM 严格过滤掉“导语”、“参考译文”等无关内容，只提取包含 `type` (context/question), `number`, `content`, `answer`, `analysis` 字段的 JSON。
- **中间态落地**: 将所有 Chunk 返回的 JSON 合并成一个大数组，保存为 `data/02_temp_build/{原文件名}_extracted.json`。

## 验证标准
Mock 测试并发请求，确保 JSON 组装与本地保存逻辑严密。测试通过后 Git Commit。