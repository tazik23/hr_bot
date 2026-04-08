from typing import List, Dict, Any


class DocumentChunker:
    def __init__(self, max_chunk_size: int = 1000):
        self.max_chunk_size = max_chunk_size
    
    def split(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not text or len(text.strip()) == 0:
            return []
        
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(para) > self.max_chunk_size:
                sentences = para.replace('\n', ' ').split('. ')
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current_chunk) + len(sent) < self.max_chunk_size:
                        current_chunk += sent + ". "
                    else:
                        if current_chunk:
                            chunks.append({
                                "text": current_chunk.strip(),
                                "metadata": {**metadata, "chunk_index": chunk_index}
                            })
                            chunk_index += 1
                        current_chunk = sent + ". "
            else:
                if len(current_chunk) + len(para) < self.max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "metadata": {**metadata, "chunk_index": chunk_index}
                        })
                        chunk_index += 1
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {**metadata, "chunk_index": chunk_index}
            })
        
        return chunks