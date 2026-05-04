import sqlite3
from datetime import datetime
from typing import List, Dict, Any


class StatsService:
    def __init__(self, vector_store, db_path: str = "stats.db"):
        self.vector_store = vector_store
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    has_answer BOOLEAN,
                    platform TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS top_questions (
                    question TEXT PRIMARY KEY,
                    count INTEGER
                )
            """)
    
    def record_query(self, question: str, has_answer: bool, platform: str = "unknown"):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO queries (question, has_answer, platform) VALUES (?, ?, ?)",
                (question, has_answer, platform)
            )
            conn.execute("""
                INSERT INTO top_questions (question, count) 
                VALUES (?, 1) 
                ON CONFLICT(question) DO UPDATE SET count = count + 1
            """, (question,))
    
    def get_stats(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            total_queries = cursor.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
            no_answer = cursor.execute(
                "SELECT COUNT(*) FROM queries WHERE has_answer = 0"
            ).fetchone()[0]
            
            platforms = cursor.execute(
                "SELECT platform, COUNT(*) FROM queries GROUP BY platform"
            ).fetchall()
            platform_stats = {p: c for p, c in platforms}
            
            top = cursor.execute(
                "SELECT question, count FROM top_questions ORDER BY count DESC LIMIT 10"
            ).fetchall()
            top_questions = [{"question": q, "count": c} for q, c in top]
        
        return {
            "total_documents": len(self.vector_store.get_unique_sources()),
            "total_queries": total_queries,
            "queries_without_answer": no_answer,
            "success_rate": round((total_queries - no_answer) / total_queries * 100, 1) if total_queries > 0 else 0,
            "platform_stats": platform_stats,
            "top_questions": top_questions
        }
    
    def reset_queries(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM queries")
            conn.execute("DELETE FROM top_questions")