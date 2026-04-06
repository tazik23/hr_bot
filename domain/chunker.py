from typing import List, Dict, Any


class DocumentChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not text or len(text.strip()) == 0:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
     
            if end < text_length:
                for sep in ['。', '！', '？', '.', '!', '?', '\n\n', '\n']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start:
                        end = last_sep + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk_metadata = {
                    **metadata,
                    "chunk_index": len(chunks),
                    "start_char": start,
                    "end_char": end
                }
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_metadata
                })

            start = end - self.overlap if end < text_length else end
        
        return chunks