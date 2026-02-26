import subprocess
import sys
import importlib.util
import pkg_resources
from typing import List


def check_and_install_dependencies():
    """
    检查并安装必要的依赖
    """
    required_packages = [
        "customtkinter",
        "markitdown",
        "aiohttp",
        "pytest",
        "pytest-asyncio"
    ]

    missing_packages = []

    for package in required_packages:
        if not is_package_installed(package):
            missing_packages.append(package)

    if missing_packages:
        print(f"正在安装缺失的包: {missing_packages}")
        for package in missing_packages:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ])
                print(f"✓ 成功安装 {package}")
            except subprocess.CalledProcessError:
                print(f"✗ 安装 {package} 失败")
                return False

    print("所有依赖项已就绪！")
    return True


def is_package_installed(package_name: str) -> bool:
    """
    检查包是否已安装

    Args:
        package_name: 包名

    Returns:
        bool: 是否已安装
    """
    try:
        importlib.util.find_spec(package_name)
        # 有些包的 import name 与 pip install name 不同
        if package_name == "markitdown":
            pkg_resources.get_distribution("markitdown")
        elif package_name == "customtkinter":
            pkg_resources.get_distribution("customtkinter")
        return True
    except (ImportError, pkg_resources.DistributionNotFound):
        return False


def ensure_dependencies():
    """
    确保所有依赖都已安装
    """
    if not check_and_install_dependencies():
        raise RuntimeError("无法安装必要的依赖包")