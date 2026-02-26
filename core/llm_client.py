import os
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any
from utils.file_helper import initialize_directories


class LLMClient:
    """
    动态 Few-Shot 客户端
    用于与 LLM 进行交互，提取结构化数据
    """

    def __init__(self, api_key_file: str = "API_KEY.txt"):
        self.api_key = self._load_api_key(api_key_file)
        self.base_url = "https://api.deepseek.com"  # 默认使用 DeepSeek API

    def _load_api_key(self, api_key_file: str) -> str:
        """
        从文件加载 API 密钥

        Args:
            api_key_file: API 密钥文件路径

        Returns:
            API 密钥字符串
        """
        if not os.path.exists(api_key_file):
            raise FileNotFoundError(f"API key file not found: {api_key_file}")

        with open(api_key_file, 'r', encoding='utf-8-sig') as f:
            return f.read().strip()

    def _load_few_shot_examples(self) -> tuple:
        """
        加载 Few-Shot 示例

        Returns:
            输入示例和期望输出示例
        """
        raw_template_path = "user_templates/01_raw_input.md"
        target_template_path = "user_templates/02_target_output.json"

        if not os.path.exists(raw_template_path) or not os.path.exists(target_template_path):
            # 如果模板不存在，创建默认模板
            self._create_default_templates()

        # 读取输入示例
        with open(raw_template_path, 'r', encoding='utf-8-sig') as f:
            raw_input_example = f.read()

        # 读取目标输出示例
        with open(target_template_path, 'r', encoding='utf-8-sig') as f:
            target_output_example = json.load(f)

        return raw_input_example, target_output_example

    def _create_default_templates(self):
        """
        创建默认的 Few-Shot 模板文件
        """
        template_dir = Path("user_templates")
        template_dir.mkdir(exist_ok=True)

        # 创建默认的输入示例
        default_input = """以下是选择题部分：

一、选择题
1、下列选项中，哪一个是正确的？
A. 错误选项
B. 正确选项
C. 错误选项
D. 错误选项

2、这是一道填空题
在____处填写答案。"""

        # 创建默认的目标输出示例
        default_output = [
            {
                "type": "question",
                "number": "1",
                "content": "下列选项中，哪一个是正确的？\nA. 错误选项\nB. 正确选项\nC. 错误选项\nD. 错误选项",
                "answer": "B",
                "analysis": "根据题意分析，正确答案是 B。"
            },
            {
                "type": "question",
                "number": "2",
                "content": "这是一道填空题\n在____处填写答案。",
                "answer": "适当答案",
                "analysis": "根据上下文，应该填入相应内容。"
            }
        ]

        # 写入默认输入示例
        with open("user_templates/01_raw_input.md", 'w', encoding='utf-8-sig') as f:
            f.write(default_input)

        # 写入默认输出示例
        with open("user_templates/02_target_output.json", 'w', encoding='utf-8-sig') as f:
            json.dump(default_output, f, ensure_ascii=False, indent=2)

    async def _call_llm_single(self, session: aiohttp.ClientSession, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        异步调用 LLM 处理单个块

        Args:
            session: HTTP 会话
            chunk: 要处理的数据块

        Returns:
            LLM 返回的结构化数据
        """
        # 加载 Few-Shot 示例
        raw_input_example, target_output_example = self._load_few_shot_examples()

        # 构建系统提示
        system_prompt = f"""你是一个专业的教育内容结构化助手。请将输入的题目转换为结构化的 JSON 格式。
请严格按照以下格式输出：

输入示例：
{raw_input_example}

期望输出格式示例：
{json.dumps(target_output_example, ensure_ascii=False, indent=2)}

重要要求：
1. 只提取包含题目的内容，过滤掉"导语"、"参考译文"、"注意事项"等无关内容
2. 输出的 JSON 对象必须包含以下字段：
   - type: 类型 ("context" 表示背景材料，"question" 表示题目)
   - number: 题号
   - content: 题目内容
   - answer: 答案
   - analysis: 解析

请直接输出 JSON 数组，不要添加任何其他解释。"""

        # 构建用户消息
        user_message = f"请将以下内容转换为结构化的 JSON 格式：\n\n{chunk['content']}"

        # 请求数据
        payload = {
            "model": "deepseek-chat",  # 使用 DeepSeek 模型
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with session.post(self.base_url + "/chat/completions", json=payload, headers=headers) as response:
                result = await response.json()

                # 解析 LLM 返回的内容
                content = result['choices'][0]['message']['content']

                # 尝试解析 JSON
                try:
                    # 清理响应内容，移除可能的 Markdown 代码块标记
                    content_cleaned = content.strip()
                    if content_cleaned.startswith('```json'):
                        content_cleaned = content_cleaned[7:]  # 移除 ```json
                    if content_cleaned.endswith('```'):
                        content_cleaned = content_cleaned[:-3]  # 移除 ```

                    extracted_data = json.loads(content_cleaned)
                    return extracted_data
                except json.JSONDecodeError:
                    # 如果解析失败，返回错误信息
                    return {
                        "error": f"Failed to parse LLM response: {content}",
                        "original_chunk": chunk
                    }
        except Exception as e:
            return {
                "error": str(e),
                "original_chunk": chunk
            }

    async def extract_structured_data(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        并发提取结构化数据

        Args:
            chunks: 待处理的分块列表

        Returns:
            提取的结构化数据列表
        """
        # 初始化连接池
        connector = aiohttp.TCPConnector(limit=10)  # 限制并发数
        timeout = aiohttp.ClientTimeout(total=60)  # 设置超时

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 创建并发任务
            tasks = [self._call_llm_single(session, chunk) for chunk in chunks]

            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理异常情况
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "error": f"Exception occurred: {str(result)}",
                        "original_chunk": chunks[i]
                    })
                else:
                    processed_results.append(result)

            return processed_results

    def save_extracted_data(self, extracted_data: List[Dict[str, Any]], output_path: str):
        """
        保存提取的数据到 JSON 文件

        Args:
            extracted_data: 提取的数据
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

    async def process_chunks_file(self, chunks_file_path: str, output_dir: str = "data/02_temp_build"):
        """
        处理分块文件并提取结构化数据

        Args:
            chunks_file_path: 输入分块文件路径
            output_dir: 输出目录

        Returns:
            提取结果及输出文件路径
        """
        # 读取分块文件
        with open(chunks_file_path, 'r', encoding='utf-8-sig') as f:
            chunks = json.load(f)

        # 提取结构化数据
        extracted_data = await self.extract_structured_data(chunks)

        # 生成输出路径
        file_name = Path(chunks_file_path).stem.replace('_chunks', '')
        output_path = Path(output_dir) / f"{file_name}_extracted.json"

        # 确保输出目录存在
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 保存提取结果
        self.save_extracted_data(extracted_data, str(output_path))

        return {
            'extracted_data': extracted_data,
            'output_path': str(output_path)
        }