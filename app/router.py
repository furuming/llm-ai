"""HTTPリクエストのルーティングを担当するモジュール。"""
from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Callable, Dict, Tuple


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


def create_router() -> Router:
    """アプリケーション既定のルーティング設定を生成する。"""
    router = Router()

    # ここにルートを登録する
    router.add_route("GET", "/hello", hello_handler)
    router.add_route("GET", "/temp", temp_handler)
    return router


def _write_json(handler: BaseHTTPRequestHandler, body: str, status: HTTPStatus) -> None:
    data = body.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def hello_handler(handler: BaseHTTPRequestHandler) -> None:
    """`/hello`用のレスポンスを返す。"""
    _write_json(handler, '{"message": "hello"}', HTTPStatus.OK)

def temp_handler(handler: BaseHTTPRequestHandler) -> None:
    """`/hello`用のレスポンスを返す。"""
    _write_json(handler, '{"message": "temp"}', HTTPStatus.OK)

__all__ = ["Router", "create_router"]
