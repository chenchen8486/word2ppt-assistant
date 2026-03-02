import os
import sys
from pathlib import Path


def get_application_path(relative_path: str) -> Path:
    """
    获取应用程序运行目录下的路径，无论是在开发环境还是打包后环境

    Args:
        relative_path: 相对路径

    Returns:
        应用程序目录下的实际路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        base_path = Path(sys.executable).parent
    else:
        # 如果是在开发环境中
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


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
        path = get_application_path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"确保目录存在: {path.absolute()}")


if __name__ == "__main__":
    initialize_directories()