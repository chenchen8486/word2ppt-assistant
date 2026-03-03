import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def get_resource_path(relative_path: str) -> Path:
    """
    获取资源文件的实际路径，支持 PyInstaller 打包后的环境
    注意：此函数仅用于读取打包在 _internal 中的只读资源文件

    Args:
        relative_path: 相对路径

    Returns:
        实际的文件路径
    """
    # 对于用户可写文件（config.json, data/, user_templates/），
    # 必须使用 get_application_path，指向 exe 所在目录
    # 这里保留仅用于读取模板等只读资源
    try:
        # PyInstaller 创建临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = Path(sys._MEIPASS)
        return base_path / relative_path
    except Exception:
        # 如果没有 _MEIPASS，则是在开发环境中运行
        base_path = Path.cwd()
        return base_path / relative_path


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


class ConfigManager:
    """
    配置管理器
    管理 API 密钥和其他配置设置
    """

    def __init__(self, config_path: str = None):
        if config_path is None:
            self.config_path = get_application_path("config.json")
        else:
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
                        "model": "deepseek-chat",
                        "concurrency_limit": 3
                    },
                    "qwen": {
                        "api_key": "",
                        "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                        "model": "qwen-max",
                        "concurrency_limit": 3
                    }
                },
                "settings": {
                    "default_model": "deepseek",
                    "timeout": 300,
                    "max_retries": 3
                },
                "last_used_paths": {
                    "input_folder": "",
                    "output_folder": ""
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

    def get_last_used_path(self, path_type: str) -> str:
        """
        获取上次使用的路径

        Args:
            path_type: 路径类型 ('input_folder' 或 'output_folder')

        Returns:
            上次使用的路径，如果不存在则返回空字符串
        """
        return self.config.get('last_used_paths', {}).get(path_type, "")

    def set_last_used_path(self, path_type: str, path: str):
        """
        设置上次使用的路径

        Args:
            path_type: 路径类型 ('input_folder' 或 'output_folder')
            path: 路径
        """
        if 'last_used_paths' not in self.config:
            self.config['last_used_paths'] = {}

        self.config['last_used_paths'][path_type] = str(path)
        self.save_config(self.config)

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