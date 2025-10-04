本アプリはLLMの評価を行うことを目的にwebサーバーとして以下の機能を提供する。
・利用するモデルの切り替えるAPI
・チャットAPI
・チャット処理時の速度、負荷検証結果API
・チャットの回答に対する評価API

## 環境変数の設定
- ルートディレクトリに`.env`ファイルを作成すると、`APP_HOST`や`APP_PORT`などの環境変数を起動時に自動で読み込みます。
- `.env`に記載されていない場合はOS側の環境変数が利用され、`APP_HOST`が未設定の場合は`127.0.0.1`、`APP_PORT`が未設定の場合は`8080`が既定値になります。

例:
```
APP_HOST=0.0.0.0
APP_PORT=3000
LLM_MODEL_PATH=/path/to/models/ELYZA-Llama-3-ELYZA-JP-8B-Q4_K_M.gguf
LLM_CONTEXT_SIZE=4096
```

## ローカルLLMモデルの準備
1. 既定のELYZAモデルを利用する場合は Hugging Face でモデル規約に同意し、アクセストークンを発行した上で以下を実行します。
   ```
   HF_TOKEN=hf_xxx make download-model
   ```
   `models/`配下に`ELYZA-Llama-3-ELYZA-JP-8B-Q4_K_M.gguf`が保存されます。
2. 任意のGGUFファイルを使用する場合は、[elyza/Llama-3-ELYZA-JP-8B-GGUF](https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-GGUF) から対象ファイルをダウンロードし、`models/`直下に配置するか`LLM_MODEL_PATH`にフルパスを設定してください。
3. モデルの読み込みには`llama-cpp-python`パッケージが必要です。インストールされていない場合は`pip install llama-cpp-python`を実行してください。

## サーバーの起動と確認
```
python main.py
```

別ターミナルから以下のようにアクセスするとエンドポイントを確認できます。
```
# GET /hello
curl http://127.0.0.1:8080/hello

# POST /chat
curl -X POST http://127.0.0.1:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "こんにちは", "model": "elyza/Llama-3-ELYZA-JP-8B-GGUF"}'
```

`model`を省略した場合は既定の環境変数設定が利用されます。未対応のモデルIDを指定すると503レスポンスが返ります。
モデルがロードされていない場合、`/chat`は503レスポンスでエラーメッセージを返します。
