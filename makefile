MODEL_DIR := models
MODEL_FILE := ELYZA-Llama-3-ELYZA-JP-8B-Q4_K_M.gguf
MODEL_PATH := $(MODEL_DIR)/$(MODEL_FILE)
MODEL_URL := https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-GGUF/resolve/main/$(MODEL_FILE)?download=1

ifdef HF_TOKEN
CURL_AUTH := -H "Authorization: Bearer $(HF_TOKEN)"
endif

.PHONY: run
run:
	python main.py

.PHONY: download-model
# 既定のELYZAモデルをダウンロードする
download-model: $(MODEL_PATH)

$(MODEL_PATH):
	@mkdir -p $(MODEL_DIR)
	curl -fL $(CURL_AUTH) -o "$@" "$(MODEL_URL)"
