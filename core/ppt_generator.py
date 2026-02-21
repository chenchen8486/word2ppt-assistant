import os
import subprocess
import threading
from utils.marp_manager import MarpManager

class PPTGenerator:
    def __init__(self):
        self.marp_manager = MarpManager()
        self.marp_exe = None

    def generate_pptx(self, marp_content, output_file):
        """
        Generates a PPTX file from Marp Markdown content.
        """
        # Ensure Marp CLI is available
        if not self.marp_exe:
            self.marp_exe = self.marp_manager.ensure_marp_cli()

        # Add Front-matter
        full_content = f"""---
marp: true
theme: default
paginate: true
size: 16:9
---

{marp_content}
"""
        
        # Write to temp file
        temp_md = "temp_slides.md"
        with open(temp_md, "w", encoding="utf-8") as f:
            f.write(full_content)
            
        try:
            # Call Marp CLI
            # marp.exe temp_slides.md --pptx -o output.pptx
            cmd = [
                self.marp_exe,
                temp_md,
                "--pptx",
                "-o", output_file,
                "--allow-local-files" # Important for local images
            ]
            
            # Run subprocess
            # Capture output for debugging
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"Marp Output: {result.stdout}")
            return True, "PPTX generated successfully."
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Marp Error: {e.stderr}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
        finally:
            # Cleanup temp file if desired, or keep for debugging
            if os.path.exists(temp_md):
                try:
                    os.remove(temp_md)
                except:
                    pass
