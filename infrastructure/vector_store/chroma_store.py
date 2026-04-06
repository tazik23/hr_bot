from typing import List, Dict, Any
import chromadb

from domain.vector_store import VectorStore


class ChromaStore(VectorStore):
    def __init__(self, collection_name: str = "hr_documents"):
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.client.get_or_create_collection(collection_name)
    
    def add_documents(
        self, 
        texts: List[str], 
        embeddings: List[List[float]], 
        metadatas: List[Dict[str, Any]]
    ) -> None:
        ids = [f"doc_{i}" for i in range(len(texts))]
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if not results['documents'] or not results['documents'][0]:
            return []
        
        documents = []
        for i in range(len(results['documents'][0])):
            documents.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "score": results['distances'][0][i] if results['distances'] else 0
            })
        
        return documents
    
    def delete_by_source(self, source: str) -> int:
        results = self.collection.get(
            where={"source": source}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        
        return 0
    
    def get_unique_sources(self) -> List[str]:
        results = self.collection.get()
        sources = set()
        for metadata in results['metadatas']:
            if metadata and 'source' in metadata:
                sources.add(metadata['source'])
        return list(sources)
    
    def count(self) -> int:
        return self.collection.count()