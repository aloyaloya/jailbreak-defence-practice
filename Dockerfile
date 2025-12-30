FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY signatures.json .
COPY dataset.csv .
COPY ingest.py .
COPY train_head.py .
COPY export_onnx.py .
COPY main.py .

RUN mkdir -p models chroma_db

COPY models/ ./models/
COPY classifier.pkl ./

COPY chroma_db/ ./chroma_db/ 2>/dev/null || true

ENV DRY_RUN=False
ENV AUDIT_LOG_PATH=/app/audit.jsonl
ENV HF_HUB_DISABLE_XET=1
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV TRANSFORMERS_OFFLINE=1
ENV HF_DATASETS_OFFLINE=1
ENV HF_HUB_OFFLINE=1

EXPOSE 8000

CMD ["python", "main.py"]

