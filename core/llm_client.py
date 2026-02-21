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
        Splits text into chunks based on major section headers.
        Uses regex: r'(^#*\s*[*]*[一二三四五六七八九十]+[、．].*?$)'
        """
        # Improved Regex for better robustness
        pattern = r'(^#*\s*[*]*[一二三四五六七八九十]+[、．].*?$)'
        
        parts = re.split(pattern, text, flags=re.MULTILINE)
        
        chunks = []
        
        # The first part might be introductory text before any header
        if parts and len(parts) > 0:
            first_part = parts[0]
            if first_part.strip():
                 chunks.append(first_part)
            parts = parts[1:]
            
        # Iterate through the rest
        for i in range(0, len(parts), 2):
            header = parts[i] if i < len(parts) else ""
            content = parts[i+1] if i+1 < len(parts) else ""
            
            chunk_text = header + content
            if chunk_text.strip():
                chunks.append(chunk_text)
                
        if not chunks:
            return [text]
            
        return chunks

    def generate_marp_content(self, chunk_text, system_prompt=None):
        """
        Sends the chunk to LLM and gets the Marp Markdown content.
        """
        import time
        
        if not system_prompt:
            system_prompt = """
你是一个顶级的教育课件排版专家。请将用户输入的试卷 Chunk（包含一道大题及旗下小题），重写为符合 Marp 语法的 Markdown 代码。
严格遵守以下排版与抽取规则：
1. **分页限制**：使用 `---` 分隔每一页幻灯片。文字绝不能溢出屏幕！
2. **结构紧凑 (1-2页原则)**：
   - 每道小题的完整结构必须是：题目 -> 答案 -> 解析。
   - 尽可能将同一道小题的“题+答+解析”放在同一页内。如果解析过长，允许将“解析”单独放在下一页。
3. **字号与视觉层级控制**：
   - 大题标题与字号统一，小题字号统一。
   - **大段背景描述**：大题的背景材料必须单独放一页，并且强制使用 HTML 标签 `<small>` 或 `<span style="font-size: 80%">` 包裹，缩小字号以防止溢出。
   - **小题主体**：使用标准的 Markdown 标题（如 `### 1. 题目`）保持稍大字号。
4. **图文排版**：如果文本中提到图片（如 [image1.png]），请使用 Marp 图片语法 `![bg right:40% fit](temp_images/image1.png)` 进行左右分栏排版。
5. **严禁篡改与漏题**：必须 100% 保留原文的每一个字，严禁总结缩写，只允许调整排版标记。
6. **纯净输出**：不要输出任何非 Marp 代码的解释性文字，不要加上 ```markdown 代码块标记。只输出幻灯片页面内容。
"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": chunk_text}
                    ],
                    stream=False
                )
                
                content = response.choices[0].message.content.strip()
                # 剔除首尾的代码块标记
                if content.startswith("```markdown"):
                    content = content[11:].strip()
                elif content.startswith("```"):
                    content = content[3:].strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
                return content
                
            except Exception as e:
                print(f"Error calling LLM (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return f"<!-- Error processing chunk after {max_retries} attempts: {e} -->\n\n{chunk_text}"
