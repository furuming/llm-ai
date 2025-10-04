"""アプリケーション設定の読み込みを支援するモジュール。"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from .env_loader import load_env


@dataclass(frozen=True)
class Config:
    host: str
    port: int

    @classmethod
    def from_env(cls) -> "Config":
        """環境変数から設定オブジェクトを構築する。"""
        return cls(host=_read_host(), port=_read_port())


def load_config(dotenv_path: str = ".env", override: bool = False) -> Config:
    """`.env`とOS環境変数を読み込み`Config`を生成する。"""
    load_env(dotenv_path=dotenv_path, override=override)
    return Config.from_env()


def _read_host(default: str = "127.0.0.1") -> str:
    host = os.getenv("APP_HOST")
    if not host:
        return default
    return host


def _read_port(default: Optional[int] = 8080) -> int:
    raw_port = os.getenv("APP_PORT")
    if not raw_port:
        return int(default) if default is not None else 0

    try:
        return int(raw_port)
    except ValueError:
        return int(default) if default is not None else 0


__all__ = ["Config", "load_config"]
