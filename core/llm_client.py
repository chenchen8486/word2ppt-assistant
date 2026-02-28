import os
import json
import asyncio
import aiohttp
import re
from pathlib import Path
from typing import List, Dict, Any
from utils.file_helper import initialize_directories
from utils.config_manager import ConfigManager


class LLMClient:
    """
    动态 Few-Shot 客户端
    用于与 LLM 进行交互，提取结构化数据
    """

    def __init__(self, model_name: str = None, config_path: str = "config.json"):
        self.config_manager = ConfigManager(config_path)
        self.model_name = model_name or self.config_manager.get_default_model()
        self.api_key = self.config_manager.get_api_key(self.model_name)

        if not self.api_key:
            raise ValueError(f"No API key configured for model: {self.model_name}")

        model_config = self.config_manager.get_model_config(self.model_name)
        self.base_url = model_config.get('endpoint', 'https://api.deepseek.com')
        self.model = model_config.get('model', 'deepseek-chat')

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

    def _clean_response_content(self, content: str) -> str:
        """清理 LLM 响应内容，安全截取 JSON 数组或对象"""
        content_cleaned = content.strip()

        # 寻找第一个 [ 和最后一个 ]
        start_idx = content_cleaned.find('[')
        end_idx = content_cleaned.rfind(']')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return content_cleaned[start_idx:end_idx+1]

        # 容错：如果不是数组，尝试寻找对象 {}
        start_idx = content_cleaned.find('{')
        end_idx = content_cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return content_cleaned[start_idx:end_idx+1]

        return content_cleaned

    def _validate_json_structure(self, data: Any) -> bool:
        """
        验证提取的数据结构是否符合要求

        Args:
            data: 要验证的数据

        Returns:
            是否符合要求
        """
        if not isinstance(data, list):
            return False

        for item in data:
            if not isinstance(item, dict):
                return False

            # 检查必需字段
            required_fields = ['type', 'number', 'content']
            for field in required_fields:
                if field not in item:
                    return False

            # 验证 type 值
            item_type = item.get('type', '').lower()
            if item_type not in ['context', 'question']:
                return False

            # 如果是 question 类型，检查额外字段
            if item_type == 'question':
                if 'answer' not in item or 'analysis' not in item:
                    return False

        return True

    def _repair_item_structure(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复单个项目的结构

        Args:
            item: 要修复的项目

        Returns:
            修复后的项目
        """
        # 确保必需字段存在
        item.setdefault('type', 'question')
        item.setdefault('number', '')
        item.setdefault('content', '')

        # 确保类型值有效
        if item['type'].lower() not in ['context', 'question']:
            item['type'] = 'question'

        # 对于 question 类型，确保 answer 和 analysis 存在
        if item['type'].lower() == 'question':
            item.setdefault('answer', '')
            item.setdefault('analysis', '')

        # 对于 context 类型，也可以提供默认的 answer 和 analysis
        if item['type'].lower() == 'context':
            item.setdefault('answer', '')
            item.setdefault('analysis', '')

        return item

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
   - answer: 答案 (question类型必须有)
   - analysis: 解析 (question类型必须有)
3. 你必须且只能输出合法的 JSON 数组。绝对禁止在 JSON 字符串内部使用 \\_, \\* 等非法的 Markdown 转义字符！ 遇到填空横线直接输出 ___ 即可。
4. 如果输入内容是背景材料（如"一、"、"二、"开头的内容），请将其标记为"type": "context"，否则标记为"type": "question"
5. 请确保所有字段都正确填充，不要留空。如果缺少答案或解析，基于内容进行合理的推断。

请直接输出 JSON 数组，不要添加任何其他解释。"""

        # 构建用户消息
        user_message = f"请将以下内容转换为结构化的 JSON 格式：\n\n{chunk['content']}"

        # 请求数据
        payload = {
            "model": self.model,  # 使用配置中的模型
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1,
            "max_tokens": 8192  # 必须新增此参数，防止长文本截断
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with session.post(self.base_url + "/chat/completions", json=payload, headers=headers) as response:
                result = await response.json()

                # 根据不同的模型类型解析响应
                content = None

                if self.model_name == "qwen":
                    # 阿里云通义千问的响应格式
                    if 'output' in result and 'choices' in result['output']:
                        content = result['output']['choices'][0].get('message', {}).get('content', '')
                    elif 'result' in result:
                        content = result['result']
                else:
                    # DeepSeek 或其他兼容 OpenAI 格式的模型
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                    else:
                        # 尝试不同的响应格式
                        if 'data' in result and 'choices' in result['data']:
                            content = result['data']['choices'][0]['message']['content']
                        elif 'response' in result:
                            content = result['response']

                if content is None:
                    return {
                        "error": f"Unable to parse API response: {result}",
                        "original_chunk": chunk
                    }

                # 尝试解析 JSON
                try:
                    # 使用新增的清理函数
                    content_cleaned = self._clean_response_content(content)

                    extracted_data = json.loads(content_cleaned)

                    # 验证结构并修复
                    if isinstance(extracted_data, list):
                        validated_data = []
                        for item in extracted_data:
                            if isinstance(item, dict):
                                # 修复单个项目结构
                                repaired_item = self._repair_item_structure(item)

                                # 验证修复后的项目
                                required_fields = ['type', 'number', 'content']
                                valid = all(field in repaired_item for field in required_fields)

                                if valid:
                                    validated_data.append(repaired_item)
                                else:
                                    # 如果修复后仍不完整，记录错误
                                    validated_data.append({
                                        "error": f"Item missing required fields after repair: {item}",
                                        "original_chunk": chunk
                                    })
                            else:
                                # 非字典项视为错误
                                validated_data.append({
                                    "error": f"Non-dict item in extracted data: {item}",
                                    "original_chunk": chunk
                                })

                        return validated_data
                    else:
                        # 单个对象的情况
                        if isinstance(extracted_data, dict):
                            repaired_item = self._repair_item_structure(extracted_data)

                            required_fields = ['type', 'number', 'content']
                            if all(field in repaired_item for field in required_fields):
                                return [repaired_item]
                            else:
                                return [{
                                    "error": f"Single item missing required fields after repair: {extracted_data}",
                                    "original_chunk": chunk
                                }]
                        else:
                            return {
                                "error": f"Invalid data type from LLM: {type(extracted_data)}",
                                "original_chunk": chunk
                            }

                except json.JSONDecodeError as e:
                    # 如果解析失败，记录详细错误信息
                    print(f"JSON解析错误: {e}")
                    print(f"原始内容: {repr(content)}")
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
        connector = aiohttp.TCPConnector(limit=3)  # 限制并发数为 3，防止 API 厂商限流拉黑
        timeout = aiohttp.ClientTimeout(total=300)  # 将超时时间放宽到 300 秒 (5分钟)，给大模型充分的生成时间

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
        raw_extracted_data = await self.extract_structured_data(chunks)

        # 展平列表，并暴露错误
        extracted_data = []
        for item in raw_extracted_data:
            if isinstance(item, list):
                extracted_data.extend(item)
            elif isinstance(item, dict):
                if "error" in item:
                    # 遇到错误，生成一个显眼的错误条目占位，绝不能静默丢弃！
                    extracted_data.append({
                        "type": "context",
                        "number": "⚠️提取失败",
                        "content": f"错误信息: {item['error']}",
                        "answer": "",
                        "analysis": f"原始数据块预览: {str(item.get('original_chunk', ''))[:150]}..."
                    })
                else:
                    extracted_data.append(item)

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