import sqlite3
from typing import Optional, List, Dict
from datetime import datetime
from core.models import FocusSession, SessionStatus 


class FocusRepository: #Создаём нового кладовщика 
    def __init__(self, db_path: str = "focus_sessions.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):  #Аналогия кладовщик заходит на склад и говорит id - номер таблицы user_id - чья коробка, started_at - когда начали
        """Создаем таблицу если её нет"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    ended_at TIMESTAMP,
                    planned_duration_min INTEGER NOT NULL,
                    actual_duration_min INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    CHECK (status IN ('active', 'completed', 'canceled'))
                )
            """)
            conn.commit()
    
    def create_session(self, user_id: int, minutes: int) -> FocusSession:
        """Создаем новую сессию"""
        session = FocusSession(
            user_id=user_id,
            started_at=datetime.now(),
            planned_duration_min=minutes,
            status=SessionStatus.active
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions 
                (user_id, started_at, planned_duration_min, status) 
                VALUES (?, ?, ?, ?) 
            """, (user_id, session.started_at, minutes, SessionStatus.active.value)) # Кладём коробку на склад, заполняем номер полки
            
            session.id = cursor.lastrowid
        
        return session
    
    def get_active_session(self, user_id: int) -> Optional[FocusSession]:
        """Получаем активную сессию пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE user_id = ? AND status = 'active'
                ORDER BY started_at DESC
                LIMIT 1
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_session(row)
    
    def complete_session(self, session_id: int):
        """Завершаем сессию успешно"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET status = 'completed', ended_at = ?
                WHERE id = ?
            """, (datetime.now(), session_id))
            conn.commit()
    
    def cancel_session(self, session_id: int):
        """Отменяем сессию"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions 
                SET status = 'canceled', ended_at = ?
                WHERE id = ?
            """, (datetime.now(), session_id))
            conn.commit()
    
    def get_user_stats(self, user_id: int, period: str = "today") -> dict:
        """Статистика по пользователю"""
        # Этот метод нужно будет доработать для разных периодов
        with sqlite3.connect(self.db_path) as conn: # Это контестный менеджер он автоматически закрывает соеденине с БД
            cursor = conn.cursor()
            
            # Пример для сегодня
            cursor.execute("""
                SELECT 
                    COUNT(*) as session_count,
                    SUM(planned_duration_min) as total_minutes
                FROM sessions 
                WHERE user_id = ? 
                AND DATE(started_at) = DATE('now')
                AND status = 'completed'
            """, (user_id,))
            
            result = cursor.fetchone()
            return {
                "sessions": result[0] or 0,
                "total_minutes": result[1] or 0
            }
    
    def _row_to_session(self, row) -> FocusSession: # распаковывать коробку 
        """Конвертируем строку БД в объект Session"""
        return FocusSession(
            id=row['id'],
            user_id=row['user_id'],
            started_at=datetime.fromisoformat(row['started_at']),
            ended_at=datetime.fromisoformat(row['ended_at']) if row['ended_at'] else None,
            planned_duration_min=row['planned_duration_min'],
            actual_duration_min=row['actual_duration_min'],
            status=SessionStatus(row['status'])
        )