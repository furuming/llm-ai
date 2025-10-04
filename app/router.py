"""HTTPリクエストのルーティングを担当するモジュール。"""
from __future__ import annotations

import json
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Callable, Dict, Tuple
from urllib.parse import urlsplit

from config.config import Config

Handler = Callable[[BaseHTTPRequestHandler], None]


class Router:
    """HTTPメソッドとパスに応じて処理関数を振り分けるルーター。"""

    def __init__(self) -> None:
        self._routes: Dict[Tuple[str, str], Handler] = {}

    def add_route(self, method: str, path: str, handler: Handler) -> None:
        """ルートを登録する。"""
        key = (method.upper(), path)
        self._routes[key] = handler

    def resolve(self, method: str, path: str) -> Handler | None:
        """該当ルートのハンドラーを取得する。"""
        return self._routes.get((method.upper(), path))


def create_router(config: Config | None = None) -> Router:
    """アプリケーション既定のルーティング設定を生成する。"""
    from app.controller.chat import handle_chat  # 遅延インポートで循環参照を回避

    router = Router()
    router.add_route("GET", "/hello", hello_handler)

    if config is not None:
        router.add_route("POST", "/chat", partial(handle_chat, config=config))
    else:
        router.add_route("POST", "/chat", handle_chat)

    return router


def hello_handler(handler: BaseHTTPRequestHandler) -> None:
    """`/hello`用のレスポンスを返す。"""
    write_json(handler, {"message": "hello"}, HTTPStatus.OK)


def write_json(handler: BaseHTTPRequestHandler, payload: Dict[str, object], status: HTTPStatus) -> None:
    """JSONレスポンスを送信する共通処理。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def extract_path(raw_path: str) -> str:
    """クエリを除いたパスを返す。"""
    return urlsplit(raw_path).path


__all__ = ["Router", "create_router", "write_json", "extract_path"]
