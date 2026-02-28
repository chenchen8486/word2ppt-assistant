#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据处理后自动验证脚本
此脚本应在每次数据修改后运行，以确保数据完整性
"""

import subprocess
import sys

def run_validation_after_processing():
    """运行验证并在失败时返回非零退出码"""
    try:
        result = subprocess.run([sys.executable, 'validate_data.py'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("验证失败，返回错误码:", result.returncode)
            print(result.stdout)
            print(result.stderr)
            return False
        else:
            print("验证成功！数据完整性得到保证。")
            return True
    except Exception as e:
        print(f"运行验证时发生异常: {e}")
        return False

if __name__ == "__main__":
    success = run_validation_after_processing()
    if not success:
        sys.exit(1)  # 返回错误码，便于集成到自动化流程中