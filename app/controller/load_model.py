"""ローカルLLMモデルを読み込むためのヘルパー。"""
from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from config.config import Config, load_config

try:
    from llama_cpp import Llama  # type: ignore
except ImportError:  # pragma: no cover - 実行環境依存
    Llama = None  # type: ignore[misc]


class ModelLoadError(RuntimeError):
    """モデルロードに失敗したことを示す例外。"""


_model_lock = Lock()
_model_instance: Any | None = None


def get_model(config: Optional[Config] = None) -> Any:
    """LLMモデルのシングルトンインスタンスを返す。"""
    global _model_instance

    if _model_instance is not None:
        return _model_instance

    with _model_lock:
        if _model_instance is None:
            if config is None:
                config = load_config()
            _model_instance = _initialize_model(config)

    return _model_instance


def _initialize_model(config: Config) -> Any:
    """設定をもとにモデルを初期化する。"""
    if Llama is None:
        raise ModelLoadError(
            "llama-cpp-pythonがインストールされていません。`pip install llama-cpp-python`を実行してください。"
        )

    model_path = _resolve_path(config.model_path)
    if not model_path.exists():
        raise ModelLoadError(
            f"モデルファイルが存在しません: {model_path}. `LLM_MODEL_PATH`を正しく設定してください。"
        )

    kwargs: Dict[str, Any] = {
        "model_path": str(model_path),
        "n_ctx": config.model_context,
    }
    if config.model_threads is not None:
        kwargs["n_threads"] = config.model_threads
    if config.model_gpu_layers is not None:
        kwargs["n_gpu_layers"] = config.model_gpu_layers

    try:
        return Llama(**kwargs)  # type: ignore[arg-type]
    except Exception as exc:  # pragma: no cover - llama_cpp依存
        raise ModelLoadError("モデルの初期化中にエラーが発生しました。") from exc


def _resolve_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


__all__ = ["get_model", "ModelLoadError"]
