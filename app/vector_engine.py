import os
import time
from typing import List
from sentence_transformers import SentenceTransformer

class VectorEngine:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorEngine, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if VectorEngine._model is None:
            os.environ['HF_HUB_DISABLE_XET'] = '1'
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            
            model_name = "cointegrated/rubert-tiny2"
            cache_dir = os.path.join(os.path.dirname(__file__), "..", "models")
            os.makedirs(cache_dir, exist_ok=True)
            
            try:
                snapshot_dir = os.path.join(cache_dir, "models--cointegrated--rubert-tiny2", "snapshots")
                if os.path.exists(snapshot_dir):
                    snapshots = [d for d in os.listdir(snapshot_dir) if os.path.isdir(os.path.join(snapshot_dir, d))]
                    if snapshots:
                        model_path = os.path.join(snapshot_dir, snapshots[0])
                        if os.path.exists(os.path.join(model_path, "model.safetensors")):
                            VectorEngine._model = SentenceTransformer(model_path)
                        else:
                            raise Exception(f"Файл model.safetensors не найден в {model_path}")
                    else:
                        raise Exception(f"Не найдены snapshots в {snapshot_dir}")
                elif os.path.exists(os.path.join(cache_dir, "onnx_model")):
                    VectorEngine._model = SentenceTransformer(
                        os.path.join(cache_dir, "onnx_model"),
                        model_kwargs={"provider": "CPUExecutionProvider"}
                    )
                else:
                    raise Exception(f"Модель не найдена локально. Убедитесь, что модель загружена в папку {cache_dir}/. Система работает в офлайн режиме.")
            except Exception as e:
                raise Exception(f"Не удалось загрузить модель: {e}. Убедитесь, что модель загружена в папку models/")
    
    def encode(self, text: str) -> List[float]:
        if not text:
            text = ""
        embedding = VectorEngine._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        texts = [t if t else "" for t in texts]
        embeddings = VectorEngine._model.encode(texts, convert_to_numpy=True, batch_size=32)
        return embeddings.tolist()

