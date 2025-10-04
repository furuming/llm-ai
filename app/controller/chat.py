"""チャット関連のHTTPハンドラー。"""
from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict, Optional

from config.config import Config, load_config

from .load_model import ModelLoadError, get_model

MAX_BODY_SIZE = 64 * 1024  # 64KB


class BadRequestError(ValueError):
    """リクエスト内容が不正な場合に発生する内部例外。"""


def handle_chat(handler: BaseHTTPRequestHandler, config: Config | None = None) -> None:
    """`POST /chat` のリクエストを処理する。"""
    try:
        payload = _read_json(handler)
        message = _extract_message(payload)
        model_id = _extract_model_id(payload)
    except BadRequestError as exc:
        _write_json(handler, {"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return

    if config is None:
        config = load_config()

    try:
        model = _resolve_model(model_id, config)
    except ModelLoadError as exc:
        _write_json(handler, {"error": str(exc)}, HTTPStatus.SERVICE_UNAVAILABLE)
        return

    try:
        response_text = _generate_response(model, message)
    except Exception:  # pragma: no cover - llama-cppの挙動に依存
        _write_json(handler, {"error": "モデルの推論中にエラーが発生しました。"}, HTTPStatus.INTERNAL_SERVER_ERROR)
        return

    _write_json(handler, {"message": response_text}, HTTPStatus.OK)


def _resolve_model(model_id: Optional[str], config: Config):
    """必要に応じてモデルをロードする。"""
    if model_id is None or model_id == config.model_id:
        return get_model(config)

    raise ModelLoadError(
        "指定されたモデルは現在の実装ではサポートされていません。環境変数で既定モデルを切り替えてください。"
    )


def _read_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    content_length = handler.headers.get("Content-Length")
    if content_length is None:
        raise BadRequestError("Content-Lengthヘッダーが必要です。")

    try:
        length = int(content_length)
    except ValueError as exc:
        raise BadRequestError("Content-Lengthヘッダーが不正です。") from exc

    if length <= 0:
        raise BadRequestError("リクエストボディが空です。")
    if length > MAX_BODY_SIZE:
        raise BadRequestError("リクエストボディが大きすぎます。")

    raw = handler.rfile.read(length)
    if not raw:
        raise BadRequestError("リクエストボディが空です。")

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise BadRequestError("JSONの解析に失敗しました。") from exc


def _extract_message(payload: Dict[str, Any]) -> str:
    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise BadRequestError("`message`フィールドに文字列を指定してください。")
    return message.strip()


def _extract_model_id(payload: Dict[str, Any]) -> Optional[str]:
    model_id = payload.get("model")
    if model_id is None:
        return None
    if not isinstance(model_id, str) or not model_id.strip():
        raise BadRequestError("`model`フィールドは空でない文字列を指定してください。")
    return model_id.strip()


def _generate_response(model: Any, message: str) -> str:
    if hasattr(model, "create_chat_completion"):
        result = model.create_chat_completion(  # type: ignore[attr-defined]
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
            max_tokens=256,
            temperature=0.7,
            top_p=0.95,
        )
        return _parse_chat_completion(result)

    # llama-cppの旧形式にフォールバック
    prompt = f"[INST] {message} [/INST]"
    result = model(  # type: ignore[operator]
        prompt,
        max_tokens=256,
        temperature=0.7,
        top_p=0.95,
        stop=["</s>", "[INST]"]
    )
    return _parse_completion(result)


def _parse_chat_completion(result: Dict[str, Any]) -> str:
    choices = result.get("choices")
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    return ""


def _parse_completion(result: Dict[str, Any]) -> str:
    choices = result.get("choices")
    if not choices:
        return ""
    text = choices[0].get("text")
    if isinstance(text, str):
        return text.strip()
    return ""


def _write_json(handler: BaseHTTPRequestHandler, payload: Dict[str, Any], status: HTTPStatus) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


__all__ = ["handle_chat"]
