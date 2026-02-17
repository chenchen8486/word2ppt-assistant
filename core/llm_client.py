import os
import json
import time
from openai import OpenAI, APIConnectionError, RateLimitError
import json_repair
from utils.logger import get_logger

logger = get_logger()

class LLMClient:
    """
    Client for interacting with DeepSeek API (via OpenAI SDK).
    """
    def __init__(self, api_key, base_url="https://api.deepseek.com", stop_event=None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        self.stop_event = stop_event
        self._init_client()

    def _init_client(self):
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"LLM Client initialized with Base URL: {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Client: {e}")
            raise

    def process_chunk(self, text_chunk, model="deepseek-chat", retries=3, system_prompt_override=None):
        """
        Sends a text chunk to the LLM and retrieves the structured JSON response.
        
        Args:
            text_chunk (str): The text content to process.
            model (str): The model name (e.g., "deepseek-chat", "deepseek-reasoner").
            retries (int): Number of retries for network/API errors.
            system_prompt_override (str): Optional override for system prompt.
            
        Returns:
            list: A list of objects.
        """
        system_prompt = system_prompt_override if system_prompt_override else (
            "你是一个严格的数据提取器，不是摘要助手。\n"
            "禁止总结：解析字段中的 `content` 和 `analysis` 必须完全保留原文，**一个字都不能删减**。\n"
            "完整性检查：如果你收到的文本包含 N 道题，你的 JSON 数组必须包含 N 个题目对象，**绝不能跳过任何一道题**。\n"
            "如果某道题太长，请完整保留，不要用 '...' 代替。\n\n"
            "**特别规则：关于背景材料 (Context) 与题目结构**\n"
            "如果遇到大题标题或背景材料（如'一、阅读理解'，'二、选择题'），请将其作为独立的 `context` 类型对象输出。\n"
            "紧随其后的小题（如 '1.', '2.'）作为 `question` 类型对象输出。\n"
            "**不要**将大题标题/背景材料重复包含在每个小题对象中。\n\n"
            "请将用户输入的试卷文本转换为严格的 JSON 格式列表。\n"
            "格式要求：\n"
            "1. 返回一个列表，包含多个对象。\n"
            "2. 对象类型分为两种：\n"
            "   - **背景/大题对象**：`{ \"type\": \"context\", \"content\": \"...\" }`\n"
            "   - **题目对象**：`{ \"type\": \"question\", \"id\": \"题号\", \"question\": \"具体问题文本\", \"options\": [\"A. xxx\", \"B. xxx\"], \"answer\": \"答案\", \"analysis\": \"解析\" }`\n"
            "3. 不要输出任何 Markdown 标记（如 ```json），直接输出 JSON 字符串。\n"
            "4. 必须确保 JSON 格式合法。\n"
            "5. 如果文本仅包含背景材料而没有题目，请仅返回背景对象。\n"
            "6. 如果文本不包含任何有效内容，返回空列表 []。"
        )

        for attempt in range(retries):
            if self.stop_event and self.stop_event.is_set():
                logger.info("Task stopped by user during retry loop.")
                return []

            try:
                logger.info(f"Sending chunk to AI (Attempt {attempt + 1}/{retries})...")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text_chunk}
                    ],
                    stream=False,
                    temperature=0.1  # Low temperature for deterministic output
                )
                
                content = response.choices[0].message.content
                logger.debug(f"AI Response content (truncated): {content[:200]}...")
                
                # Parse JSON
                parsed_data = self._parse_json(content)
                if parsed_data is not None:
                    logger.info(f"Successfully parsed {len(parsed_data)} questions from chunk.")
                    return parsed_data
                else:
                    logger.warning("Failed to parse JSON from AI response.")
                    # Don't retry immediately if it's a parsing error, but maybe the AI just hallucinated.
                    # We continue to retry in case a different generation helps.
            
            except (APIConnectionError, RateLimitError) as e:
                logger.error(f"API Error: {e}")
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error("Max retries reached.")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error during API call: {e}")
                raise

        return []

    def _parse_json(self, content):
        """
        Attempts to parse JSON string, using json_repair if standard parsing fails.
        """
        # Clean up markdown code blocks if present
        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
            
        cleaned_content = cleaned_content.strip()

        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            logger.warning("Standard JSON parsing failed. Attempting repair...")
            try:
                repaired_object = json_repair.repair_json(cleaned_content, return_objects=True)
                return repaired_object
            except Exception as e:
                logger.error(f"JSON Repair failed: {e}")
                logger.error(f"Original content causing error: {content}")
                return None

if __name__ == "__main__":
    # Test block
    pass
