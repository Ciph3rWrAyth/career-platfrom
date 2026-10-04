# Та же версия Python, что и локально. slim — без лишнего веса.
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_REPO=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
    MODEL_DIR=/app/models/minilm

WORKDIR /app

# 1) CPU-сборка torch отдельным индексом.
#    С PyPI по умолчанию прилетает вариант с CUDA весом в несколько гигабайт.
RUN pip install --no-cache-dir torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu

# 2) Остальные зависимости. torch нужной версии уже стоит, pip его пропустит.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Веса модели запекаем в образ на этапе сборки, ревизия зафиксирована.
#    В рантайме сеть для модели уже не нужна.
ARG MODEL_REVISION=e8f8c211226b894fcb81acc59f3b34ba3efd5f42
RUN python -c "import os; from huggingface_hub import snapshot_download; snapshot_download(os.environ['MODEL_REPO'], revision=os.environ['MODEL_REVISION'], local_dir=os.environ['MODEL_DIR'], ignore_patterns=['onnx/*','openvino/*','*.h5','pytorch_model.bin'])"

# 4) Код приложения (venv и .env не попадут — они в .dockerignore)
COPY . .

EXPOSE 8000

# Один процесс, без --reload (Блок 11).
# host 0.0.0.0 обязателен: иначе порт не виден за пределами контейнера.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
