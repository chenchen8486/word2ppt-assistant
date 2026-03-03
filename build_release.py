#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Word2PPT-Assistant 自动化构建脚本

此脚本用于自动执行以下流程：
1. 清理旧的 build/ 和 dist/ 目录
2. 执行 PyInstaller 构建
3. 装配发布包（复制 config.json、user_templates/，创建 data/ 目录结构）
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_info(message: str):
    """打印信息消息"""
    print(f"\n[INFO] {message}")


def print_success(message: str):
    """打印成功消息"""
    print(f"\n[SUCCESS] {message}")


def print_error(message: str):
    """打印错误消息"""
    print(f"\n[ERROR] {message}")


def cleanup():
    """清理旧的 build 和 dist 目录"""
    print_info("开始清理旧的构建文件...")

    # 定义需要清理的目录
    dirs_to_clean = [
        "build",
        "dist",
        "__pycache__",
    ]

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print_info(f"已删除目录: {dir_name}")
            except Exception as e:
                print_error(f"删除目录 {dir_name} 失败: {e}")

    # 删除 .spec 文件（会重新生成）
    if os.path.exists("Word2PPT-Assistant.spec"):
        try:
            os.remove("Word2PPT-Assistant.spec")
            print_info("已删除旧的 spec 文件")
        except Exception as e:
            print_error(f"删除 spec 文件失败: {e}")

    print_success("清理完成！")


def build_exe():
    """执行 PyInstaller 构建"""
    print_info("开始执行 PyInstaller 构建...")

    # 构建命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onedir",           # 单目录模式
        "--windowed",         # 隐藏控制台窗口
        "--name=Word2PPT-Assistant",  # 应用程序名称
        "--clean",            # 清理缓存
        "--noconfirm",        # 覆盖输出目录不询问
        "--add-data=user_templates;user_templates",  # 包含 user_templates
        "--add-data=config.json;.",                   # 包含 config.json 到根目录
        "--collect-all=customtkinter",                # 收集 customtkinter 资源
        "--collect-data=magika",                      # 收集 magika 模型
        "--hidden-import=pptx",                       # 隐藏导入 pptx
        "main.py"
    ]

    print_info(f"执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,  # 直接输出到控制台
            text=True
        )
        print_success("PyInstaller 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"PyInstaller 构建失败: {e}")
        print_error(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"构建过程发生异常: {e}")
        return False


def copy_file(src: Path, dst: Path):
    """复制文件，自动创建目标目录"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_directory(src: Path, dst: Path):
    """复制目录，自动创建目标目录"""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        s = src / item.name
        d = dst / item.name
        if s.is_dir():
            copy_directory(s, d)
        else:
            copy_file(s, d)


def assemble_release():
    """装配发布包"""
    print_info("开始装配发布包...")

    release_dir = Path("dist/Word2PPT-Assistant")

    if not release_dir.exists():
        print_error(f"构建产物目录不存在: {release_dir.absolute()}")
        return False

    # 1. 复制 config.json
    config_src = Path("config.json")
    config_dst = release_dir / "config.json"
    if config_src.exists():
        copy_file(config_src, config_dst)
        print_info(f"已复制 config.json 到 {config_dst.absolute()}")
    else:
        print_error("config.json 不存在！")

    # 2. 复制 user_templates 目录
    templates_src = Path("user_templates")
    templates_dst = release_dir / "user_templates"
    if templates_src.exists():
        copy_directory(templates_src, templates_dst)
        print_info(f"已复制 user_templates/ 到 {templates_dst.absolute()}")
    else:
        print_error("user_templates/ 目录不存在！")

    # 3. 创建 data/ 目录结构
    data_dirs = [
        release_dir / "data" / "01_input_docs",
        release_dir / "data" / "02_temp_build",
        release_dir / "data" / "03_output_pptx",
    ]

    for data_dir in data_dirs:
        data_dir.mkdir(parents=True, exist_ok=True)
        print_info(f"已创建目录: {data_dir.absolute()}")

    # 4. 验证发布包结构
    print_info("\n验证发布包结构:")
    required_files = [
        "Word2PPT-Assistant.exe",
        "config.json",
        "user_templates/01_raw_input.md",
        "user_templates/02_target_output.json",
        "data/01_input_docs",
        "data/02_temp_build",
        "data/03_output_pptx",
    ]

    all_ok = True
    for rel_path in required_files:
        full_path = release_dir / rel_path
        exists = full_path.exists() if '/' not in rel_path else full_path.parent.exists()
        status = "[OK]" if exists else "[MISSING]"
        print_info(f"  {status} {rel_path}")
        if not exists:
            all_ok = False

    if all_ok:
        print_success("发布包装配完成！")
        return True
    else:
        print_error("发布包装配不完整！")
        return False


def show_release_info():
    """显示发布信息"""
    print_info("\n" + "=" * 60)
    print_info("发布包信息:")
    print_info("=" * 60)

    release_dir = Path("dist/Word2PPT-Assistant")
    if release_dir.exists():
        # 获取可执行文件大小
        exe_path = release_dir / "Word2PPT-Assistant.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print_info(f"  主程序: Word2PPT-Assistant.exe ({size_mb:.1f} MB)")

        # 获取总大小
        total_size = sum(f.stat().st_size for f in release_dir.rglob('*') if f.is_file())
        print_info(f"  总大小: {total_size / (1024 * 1024):.1f} MB")

        # 获取目录结构
        print_info("\n  目录结构:")
        for item in sorted(release_dir.iterdir()):
            if item.is_dir():
                print_info(f"    {item.name}/")
            else:
                print_info(f"    {item.name}")

    print_info("\n使用说明:")
    print_info("  1. 直接运行 dist/Word2PPT-Assistant/Word2PPT-Assistant.exe")
    print_info("  2. config.json 位于 .exe 同级目录，可编辑配置")
    print_info("  3. user_templates/ 位于 .exe 同级目录，可修改模板")
    print_info("  4. data/ 目录用于存放输入和输出文件")
    print_info("")


def main(auto_confirm: bool = False):
    """主函数

    Args:
        auto_confirm: 是否自动确认构建，True 时跳过用户确认直接构建
    """
    print_info("=" * 60)
    print_info("Word2PPT-Assistant 自动化构建脚本")
    print_info("=" * 60)

    # 询问用户是否继续
    try:
        if not auto_confirm:
            response = input("\n是否继续构建? (y/n): ").strip().lower()
            if response != 'y':
                print_info("构建已取消")
                return
        else:
            print_info("自动确认模式，直接开始构建...")

        # 清理
        cleanup()

        # 构建
        if not build_exe():
            print_error("构建失败，退出")
            sys.exit(1)

        # 装配
        if not assemble_release():
            print_error("装配失败，退出")
            sys.exit(1)

        # 显示信息
        show_release_info()

        print_success("=" * 60)
        print_success("构建完成！发布包位置: dist/Word2PPT-Assistant/")
        print_success("=" * 60)

    except KeyboardInterrupt:
        print_info("\n构建已取消")
        sys.exit(0)
    except Exception as e:
        print_error(f"构建过程发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # 支持命令行参数 --yes 自动确认
    auto_confirm = "--yes" in sys.argv
    main(auto_confirm=auto_confirm)
