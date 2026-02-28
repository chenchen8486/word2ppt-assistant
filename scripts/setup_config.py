#!/usr/bin/env python3
"""
API 密钥配置助手
用于帮助用户在 config.json 中设置 API 密钥
"""

import json
from pathlib import Path
from getpass import getpass


def main():
    print("=" * 50)
    print("Word2PPT Assistant - API 密钥配置助手")
    print("=" * 50)

    config_path = Path("config.json")

    # 读取现有配置
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
    else:
        print(f"错误: 找不到配置文件 {config_path}")
        return

    print("\n可用的模型:")
    for model_name in config.get('models', {}):
        print(f"- {model_name}")

    print("\n请输入您的 API 密钥:")

    for model_name in config.get('models', {}):
        current_key = config['models'][model_name].get('api_key', '')
        has_key = " (已配置)" if current_key else " (未配置)"

        print(f"\n{model_name}{has_key}:")
        print(f"当前状态: {'已配置' if current_key else '未配置'}")

        # 询问是否要更新密钥
        if current_key:
            update = input(f"是否要更新 {model_name} 的 API 密钥? (y/N): ").lower().strip()
            if update != 'y':
                continue

        # 获取新的 API 密钥
        api_key = getpass(f"请输入 {model_name} 的 API 密钥: ")

        if api_key:
            config['models'][model_name]['api_key'] = api_key
            print(f"✓ {model_name} 的 API 密钥已更新")
        else:
            print(f"✗ 未输入 {model_name} 的 API 密钥")

    # 保存配置
    with open(config_path, 'w', encoding='utf-8-sig') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 配置已保存到 {config_path}")
    print("\n配置完成! 您现在可以运行主程序了。")


if __name__ == "__main__":
    main()