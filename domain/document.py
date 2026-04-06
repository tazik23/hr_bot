from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class Document:
    filename: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if "uploaded_at" not in self.metadata:
            self.metadata["uploaded_at"] = datetime.now().isoformat()
        if "source" not in self.metadata:
            self.metadata["source"] = self.filename