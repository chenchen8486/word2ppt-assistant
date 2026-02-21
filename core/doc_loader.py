import os
import zipfile
import re
from markitdown import MarkItDown

class DocLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_images_dir = "temp_images"
        os.makedirs(self.temp_images_dir, exist_ok=True)

    def load_document(self):
        """
        Loads the document, extracts text using MarkItDown, and extracts images using zipfile.
        Returns the markdown text with appended image references.
        """
        # 1. Extract Text using MarkItDown
        md = MarkItDown()
        result = md.convert(self.file_path)
        text_content = result.text_content

        # Clean Text
        text_content = self._clean_text(text_content)

        # 2. Extract Images using zipfile
        image_files = self._extract_images()
        
        # 3. Append Image References to Text
        # We append a list of available images at the end so LLM knows what images exist.
        if image_files:
            text_content += "\n\n## Available Images\n"
            for img_path in image_files:
                # Use forward slashes for compatibility
                rel_path = img_path.replace("\\", "/")
                text_content += f"- [{os.path.basename(img_path)}]({rel_path})\n"
                
        return text_content

    def _clean_text(self, text):
        """
        Cleans the extracted text by removing unnecessary headers and footers.
        """
        # 1. 兼容带有加粗符号的第一个大题标题 (如 **一、**)
        match = re.search(r'(^#*\s*[*]*[一二三四五六七八九十]+[、．])', text, flags=re.MULTILINE)
        if match:
            start_index = match.start()
            text = text[start_index:]
            
        # 2. 移除 "【导语】" 段落
        text = re.sub(r'^.*【导语】.*$', '', text, flags=re.MULTILINE)
        
        # 3. 智能移除“参考译文”区块 (修复吃掉下半张试卷的Bug，兼容 [*]*)
        pattern_ref = r'参考译文.*?(?=\n#*\s*[*]*[一二三四五六七八九十]+[、．]|\n#*\s*[*]*第[一二三四五六七八九十ⅠⅡIIIIVV]+卷|$)'
        text = re.sub(pattern_ref, '', text, flags=re.DOTALL)
            
        return text.strip()

    def _extract_images(self):
        """
        Extracts images from the .docx file (which is a zip) to temp_images directory.
        Returns a list of paths to the extracted images.
        """
        image_paths = []
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                # Word stores images in word/media/ folder
                for file_info in zip_ref.infolist():
                    if file_info.filename.startswith('word/media/') and file_info.file_size > 0:
                        # Extract the file
                        # We want to flatten the structure or keep it simple
                        original_filename = os.path.basename(file_info.filename)
                        target_path = os.path.join(self.temp_images_dir, original_filename)
                        
                        # Write the file content
                        with open(target_path, 'wb') as f:
                            f.write(zip_ref.read(file_info))
                        
                        image_paths.append(target_path)
                        
            # Sort images to maintain order (usually image1.png, image2.png etc.)
            # This helps if we want to guess their position, though without context it's hard.
            # But the requirement says "append to end for LLM reference".
            image_paths.sort(key=lambda x: self._natural_sort_key(os.path.basename(x)))
            
        except zipfile.BadZipFile:
            print(f"Error: {self.file_path} is not a valid zip/docx file.")
        except Exception as e:
            print(f"Error extracting images: {e}")
            
        return image_paths

    def _natural_sort_key(self, s):
        """
        Sorts strings containing numbers naturally (image1, image2, image10 instead of image1, image10, image2).
        """
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', s)]
