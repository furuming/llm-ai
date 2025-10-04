from __future__ import annotations

from app.controller.load_model import ModelLoadError, get_model
from app.router import create_router
from app.server import run_server
from config.config import load_config


def main() -> None:
    """アプリケーションのCLIエントリーポイント。"""
    print("start main")

    # .envから環境変数を読み込む
    config = load_config()

    try:
        model = get_model(config)
        print(f"model loaded: {config.model_id}")
    except ModelLoadError as exc:
        print(f"モデル読み込みに失敗しました: {exc}")
        model = None

    if model is None:
        print("モデルのロードに失敗したため、推論機能は利用できません。")

    router = create_router(config=config)

    print(f"server listening on http://{config.host}:{config.port}")
    run_server(host=config.host, port=config.port, router=router)


if __name__ == "__main__":
    main()
