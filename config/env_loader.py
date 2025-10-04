"""`.env`ファイルから環境変数を読み込むユーティリティ。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def _parse_line(line: str) -> tuple[str, str] | None:
    """`KEY=VALUE`形式の1行を解析してキーと値を返す。"""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if "=" not in stripped:
        return None

    key, raw_value = stripped.split("=", 1)
    key = key.strip()
    if not key:
        return None

    value = _strip_inline_comment(raw_value.strip())
    value = _strip_quotes(value)
    value = value.replace("\\n", "\n").replace("\\r", "\r")
    return key, value


def _strip_inline_comment(value: str) -> str:
    """クォート外のインラインコメントを取り除く。"""
    in_single = False
    in_double = False
    result_chars: list[str] = []

    for char in value:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            break
        result_chars.append(char)

    return "".join(result_chars).rstrip()


def _strip_quotes(value: str) -> str:
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def load_env(dotenv_path: str | Path = ".env", override: bool = False) -> Dict[str, str]:
    """`.env`を読み込み、必要に応じて`os.environ`へ適用する。"""
    path = Path(dotenv_path)
    if not path.exists():
        return {}

    loaded: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as fp:
        for raw_line in fp:
            parsed = _parse_line(raw_line)
            if not parsed:
                continue
            key, value = parsed
            loaded[key] = value
            if override or key not in os.environ:
                os.environ[key] = value

    return loaded


__all__ = ["load_env"]
