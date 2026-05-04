from typing import List, Dict, Any
from chonkie import RecursiveChunker
from chonkie import RecursiveRules, RecursiveLevel


class DocumentChunker:
    def __init__(
        self, 
        chunk_size: int = 800,
        min_characters_per_chunk: int = 24,
        visualize: bool = False
    ):
        self.rules = RecursiveRules(
            levels=[
                RecursiveLevel(delimiters=["\n\n"], include_delim="prev"),
                RecursiveLevel(delimiters=["\n"], include_delim="prev"),
                RecursiveLevel(delimiters=[". ", "! ", "? "], include_delim="prev"),
                RecursiveLevel(delimiters=[", ", "; ", ": "], include_delim="prev"), 
                RecursiveLevel(whitespace=True)  # слова
            ]
        )
        
        self.chunker = RecursiveChunker(
            tokenizer="character", 
            chunk_size=chunk_size,
            rules=self.rules,
            min_characters_per_chunk=min_characters_per_chunk
        )
        
        self.visualize = visualize
        if visualize:
            from infrastructure.chunker_visualizer import ChunkerVisualizer
            self.viz = ChunkerVisualizer()
    
    def split(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = self.chunker.chunk(text)
        
        if not chunks:
            return []
        
        if self.visualize:
            source = metadata.get("source", "unknown")
            self.viz.print_chunks(chunks, title=f"Документ: {source}")
            self.viz.print_stats(chunks)
            self.viz.save_html(chunks, f"{source}.html")
        
        result = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            result.append({
                "text": chunk.text,
                "metadata": chunk_metadata
            })
        
        return result