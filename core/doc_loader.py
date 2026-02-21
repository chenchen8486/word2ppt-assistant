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
