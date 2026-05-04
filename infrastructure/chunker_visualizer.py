from typing import List, Dict, Any
from pathlib import Path
from chonkie import Visualizer


class ChunkerVisualizer:
    def __init__(self, output_dir: str = "chunks_viz"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.viz = Visualizer()
    
    def print_chunks(self, chunks, title: str = None):
        if title:
            print(f"\n{'='*60}")
            print(f"📊 {title}")
            print(f"{'='*60}")
        
        self.viz.print(chunks)
        print(f"\n✅ Всего чанков: {len(chunks)}")
    
    def save_html(self, chunks, filename: str = "chunks.html"):
        html_path = self.output_dir / filename
        self.viz.save(str(html_path), chunks)
        print(f"✅ HTML сохранён: {html_path}")
        return html_path
    
    def print_stats(self, chunks):
        if not chunks:
            print("❌ Нет чанков для анализа")
            return
        
        lengths = [len(chunk.text) for chunk in chunks]
        
        print(f"\n📊 Статистика чанков:")
        print(f"   Всего чанков: {len(chunks)}")
        print(f"   Средняя длина: {sum(lengths)//len(lengths)} символов")
        print(f"   Минимальная длина: {min(lengths)}")
        print(f"   Максимальная длина: {max(lengths)}")