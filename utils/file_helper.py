import os
from pathlib import Path


def initialize_directories():
    """
    初始化项目所需的目录结构
    """
    directories = [
        "data/01_input_docs",
        "data/02_temp_build",
        "data/03_output_pptx",
        "user_templates",
        "bin"
    ]

    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"确保目录存在: {path.absolute()}")


if __name__ == "__main__":
    initialize_directories()