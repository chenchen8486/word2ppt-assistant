import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    配置管理器
    管理 API 密钥和其他配置设置
    """

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if not self.config_path.exists():
            # 如果配置文件不存在，创建默认配置
            default_config = {
                "models": {
                    "deepseek": {
                        "api_key": "",
                        "endpoint": "https://api.deepseek.com",
                        "model": "deepseek-chat"
                    },
                    "qwen": {
                        "api_key": "",
                        "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                        "model": "qwen-max"
                    }
                },
                "settings": {
                    "default_model": "deepseek",
                    "timeout": 60,
                    "max_retries": 3
                }
            }
            self.save_config(default_config)
            return default_config

        with open(self.config_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    def save_config(self, config: Dict[str, Any]):
        """
        保存配置到文件

        Args:
            config: 配置字典
        """
        with open(self.config_path, 'w', encoding='utf-8-sig') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def get_api_key(self, model_name: str) -> Optional[str]:
        """
        获取指定模型的 API 密钥

        Args:
            model_name: 模型名称

        Returns:
            API 密钥，如果不存在则返回 None
        """
        if model_name in self.config.get('models', {}):
            return self.config['models'][model_name].get('api_key')
        return None

    def set_api_key(self, model_name: str, api_key: str):
        """
        设置指定模型的 API 密钥

        Args:
            model_name: 模型名称
            api_key: API 密钥
        """
        if model_name not in self.config.get('models', {}):
            self.config['models'][model_name] = {}

        self.config['models'][model_name]['api_key'] = api_key
        self.save_config(self.config)

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型的完整配置

        Args:
            model_name: 模型名称

        Returns:
            模型配置，如果不存在则返回 None
        """
        return self.config.get('models', {}).get(model_name)

    def get_default_model(self) -> str:
        """
        获取默认模型名称

        Returns:
            默认模型名称
        """
        return self.config.get('settings', {}).get('default_model', 'deepseek')

    def update_settings(self, settings: Dict[str, Any]):
        """
        更新设置

        Args:
            settings: 设置字典
        """
        if 'settings' not in self.config:
            self.config['settings'] = {}

        self.config['settings'].update(settings)
        self.save_config(self.config)