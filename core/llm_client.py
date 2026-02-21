import re
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key, model="deepseek-chat"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"  # Adjust if needed
        )
        self.model = model

    def chunk_text(self, text):
        """
        Splits text into chunks based on major section headers (e.g., ## 一、...).
        If no headers are found, returns the whole text as one chunk.
        """
        # Regex to match headers like "## 一、", "## 1.", "## Part I"
        # MarkItDown typically uses ## for level 2 headers which are often used for main sections in docs
        # We look for lines starting with ## followed by some content
        
        # Split by level 2 headers
        # We want to keep the delimiter (the header itself) with the chunk
        # re.split with capturing group keeps the delimiter
        parts = re.split(r'(^##\s+.*$)', text, flags=re.MULTILINE)
        
        chunks = []
        current_chunk = ""
        
        # The first part might be introductory text before any header
        if parts and len(parts) > 0:
            first_part = parts[0]
            if first_part.strip():
                 # If there is meaningful text before the first header, treat it as a chunk
                 chunks.append(first_part)
            # Remove the first part to align the rest as (header, content) pairs
            parts = parts[1:]

            
        # Iterate through the rest
        # parts will look like [header1, content1, header2, content2, ...]
        for i in range(0, len(parts), 2):
            header = parts[i] if i < len(parts) else ""
            content = parts[i+1] if i+1 < len(parts) else ""
            
            chunk_text = header + content
            if chunk_text.strip():
                chunks.append(chunk_text)
                
        # If no chunks were created (no headers found), return original text
        if not chunks:
            return [text]
            
        return chunks

    def generate_marp_content(self, chunk_text, system_prompt=None):
        """
        Sends the chunk to LLM and gets the Marp Markdown content.
        """
        if not system_prompt:
            system_prompt = """
你是一个幻灯片排版专家。请将用户输入的试卷内容，重写为符合 Marp 语法的 Markdown 代码。
规则：
1. 使用 `---` 分隔每一页幻灯片。
2. 每道题目必须分为两页：第一页只展示题干和选项；第二页展示完整的“题目 + 答案 + 解析”。
3. 如果遇到长文本阅读材料（背景材料），单独放在一页或多页（使用 `---` 切分），不要把它和题目挤在一起。
4. 如果提供的文本中提到图片（如 [image1.png]），请使用 Marp 的图片排版语法，如 `![bg right:40% fit](temp_images/image1.png)`，让图文并排显示。
5. 严禁漏题！严禁总结缩写！必须100%保留原文的每一个字。
6. 不要输出任何非 Marp 代码的解释性文字。
7. 输出必须包含 Marp Front-matter (虽然我会拼接，但每个部分保持独立格式较好，或者尽量只输出 body)。
   为了拼接方便，请不要输出 Front-matter (`---` at start)，只输出幻灯片页面内容。
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk_text}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"<!-- Error processing chunk: {e} -->\n\n{chunk_text}"
