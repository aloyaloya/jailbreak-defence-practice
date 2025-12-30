import os
import chromadb
from typing import List, Tuple, Optional

class VectorDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            db_path = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
            os.makedirs(db_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=db_path)
            
            try:
                self.collection = self.client.get_collection(name="threat_vectors")
            except:
                self.collection = self.client.create_collection(
                    name="threat_vectors",
                    metadata={"description": "Threat vectors database"}
                )
            
            self.initialized = True
    
    def search(self, query_vector: List[float], threshold: float = 0.35, n_results: int = 1) -> Optional[Tuple[str, float]]:
        if not query_vector:
            return None
        
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )
        
        if results['distances'] and len(results['distances'][0]) > 0:
            distance = results['distances'][0][0]
            if distance < threshold:
                return (results['ids'][0][0], distance)
        
        return None
    
    def add_vector(self, text: str, vector: List[float], metadata: dict = None):
        if metadata is None:
            metadata = {"type": "jailbreak", "risk": "high"}
        
        vector_id = f"threat_{len(self.collection.get()['ids'])}"
        
        self.collection.add(
            ids=[vector_id],
            embeddings=[vector],
            documents=[text],
            metadatas=[metadata]
        )


