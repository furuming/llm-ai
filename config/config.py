"""アプリケーション設定の読み込みを支援するモジュール。"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .env_loader import load_env

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_MODEL_PATH = _PROJECT_ROOT / "models" / "Llama-3-ELYZA-JP-8B-q4_k_m.gguf"


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    model_id: str
    model_path: str
    model_context: int
    model_threads: Optional[int]
    model_gpu_layers: Optional[int]

    @classmethod
    def from_env(cls) -> "Config":
        """環境変数から設定オブジェクトを構築する。"""
        return cls(
            host=_read_host(),
            port=_read_port(),
            model_id=_read_model_id(),
            model_path=_read_model_path(),
            model_context=_read_model_context(),
            model_threads=_read_optional_int("LLM_THREADS"),
            model_gpu_layers=_read_optional_int("LLM_GPU_LAYERS"),
        )


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


def _read_model_id(default: str = "elyza/Llama-3-ELYZA-JP-8B-GGUF") -> str:
    model_id = os.getenv("LLM_MODEL_ID")
    if not model_id:
        return default
    return model_id


def _read_model_path() -> str:
    model_path = os.getenv("LLM_MODEL_PATH")
    if not model_path:
        return str(_DEFAULT_MODEL_PATH)
    return model_path


def _read_model_context(default: int = 4096) -> int:
    raw_ctx = os.getenv("LLM_CONTEXT_SIZE")
    if not raw_ctx:
        return default
    try:
        return int(raw_ctx)
    except ValueError:
        return default


def _read_optional_int(name: str) -> Optional[int]:
    raw_value = os.getenv(name)
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError:
        return None


__all__ = [
    "Config",
    "load_config",
]
