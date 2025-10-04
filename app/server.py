"""HTTPサーバーのエントリーポイントを提供するモジュール。"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple

from .router import Router, create_router, extract_path


class AppRequestHandler(BaseHTTPRequestHandler):
    """アプリケーションのHTTPリクエストを処理するハンドラー。"""

    router: Router | None = None

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler既定メソッド)
        """GETリクエストの振る舞いを定義する。"""
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        """POSTリクエストの振る舞いを定義する。"""
        self._dispatch("POST")

    def _dispatch(self, method: str) -> None:
        router = self.router
        if router is None:
            self.send_error(500, "Router not configured")
            return

        path = extract_path(self.path)
        handler = router.resolve(method, path)
        if handler is None:
            self.send_error(404, "Not Found")
            return

        handler(self)

    def log_message(self, format: str, *args) -> None:  # noqa: A003 (親クラス定義)
        """アクセスログを標準出力へ出力する。"""
        super().log_message(format, *args)


def run_server(host: str, port: int, router: Router | None = None) -> None:
    """HTTPサーバーを起動してリクエスト待受状態にする。"""
    if router is None:
        router = create_router()

    AppRequestHandler.router = router

    server_address: Tuple[str, int] = (host, port)
    httpd = ThreadingHTTPServer(server_address, AppRequestHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


__all__ = ["run_server"]
