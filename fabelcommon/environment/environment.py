import os
from typing import Optional


def get_env_str(key: str, default: str = '') -> str:
    return os.environ.get(key, default=default)


def get_env_str_optional(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default=default)


def get_env_bool(key: str, default: bool = False) -> bool:
    value = os.environ.get(key, default=str(default)).lower()
    return value in ('true', '1', 'on', 'yes')


def get_env_int(key: str, default: int = 0) -> int:
    return int(os.environ.get(key, default=str(default)))


def get_env_float(key: str, default: float = 0.0) -> float:
    return float(os.environ.get(key, default=str(default)))
