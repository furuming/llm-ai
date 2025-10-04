from __future__ import annotations

from config.config import load_config
from app.server import run_server


def main() -> None:
    """アプリケーションのCLIエントリーポイント。"""
    print("start main")

    # .envから環境変数を読み込む
    config = load_config()

    print(f"server listening on http://{config.host}:{config.port}")
    run_server(host=config.host, port=config.port)


if __name__ == "__main__":
    main()
