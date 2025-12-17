import json #Для работы с ДЖСН файлами 
import os #Для работы с файловой системой (папки, файлы, вся хуйня короче)
from datetime import datetime # Дефолт дата и время 
from typing import List, Dict, Any, Optional #Подсказки типов

class JSONStorage:
    def __init__(self, file_path: str = 'data/sessions.json'):
        self.file_path = file_path #Путь к нашему файлу данных
        self._ensure_data_dir() 
        self._init_storage()
    
    def _ensure_data_dir(self):
        "Создаем папку data если её нет"
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        # os.makedirs - создает папку  # exist_ok=True - если папка уже есть, то тогда не выёбыватся 

    
    def _init_storage(self):
        "Создаем JSON файл с начальной структурой"
        if not os.path.exists(self.file_path):  # если файла нет
            initial_data = {
                "sessions": [],   # список всех сессий 
                "last_session_id": 0
            }
            self._save_data(initial_data)
    
    def _load_data(self) -> Dict[str, Any]:
        "Загружаем данные из JSON"
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Если файл поврежден, создаем заново, я тут хз если честно 
            self._init_storage()
            return self._load_data() # Если всё заебись пытаемся загрузить 
    
    def _save_data(self, data: Dict[str, Any]):
        "Сохраняем данные в JSON"
        with open(self.file_path, 'w', encoding='utf-8') as f:  #режим записи файла, "перезаписывает"
            json.dump(data, f, indent=2, ensure_ascii=False, default=str) #тут понятно, отступы вся хуйня 
    
    def create_session(self, user_id: int, duration_min: int) -> int:
        "Создаем новую сессию, возвращаем её ID"
        data = self._load_data()
        
        # Генерируем новый ID
        session_id = data["last_session_id"] + 1
        data["last_session_id"] = session_id
        
        # Создаем сессию
        session = {
            "id": session_id,
            "user_id": user_id,
            "started_at": datetime.now().isoformat(), # Текущее вреся как строка должна быть по идее
            "ended_at": None,
            "duration_min": duration_min,
            "status": "active"  
        }
        
        data["sessions"].append(session)
        self._save_data(data)
        return session_id
    
    def get_active_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        "Получаем активную сессию пользователя"
        data = self._load_data()
        
        for session in reversed(data["sessions"]):
            if session["user_id"] == user_id and session["status"] == "active":
                return session.copy()  # Возвращаем копию
        return None
    
    def update_session(self, session_id: int, updates: Dict[str, Any]):
        "Обновляем сессию"
        data = self._load_data()
        
        for session in data["sessions"]:
            if session["id"] == session_id:
                session.update(updates)
                # Если обновляем статус, добавляем время окончания
                if "status" in updates and updates["status"] in ["completed", "canceled"]:
                    session["ended_at"] = datetime.now().isoformat()   # ставим время окончания
                break # выходим из цикла, нашли
        
        self._save_data(data)
    
    def get_user_sessions(self, user_id: int, status: str = None) -> List[Dict[str, Any]]:
        "Получаем все сессии пользователя (можно фильтровать по статусу)"
        data = self._load_data()
        
        sessions = []
        for session in data["sessions"]:
            if session["user_id"] == user_id:
                if status is None or session["status"] == status:
                    sessions.append(session.copy())
        
        return sessions
    
    def get_user_stats(self, user_id: int, period: str = 'today') -> Dict[str, Any]:
        "Получаем статистику за период"
        from datetime import datetime, timedelta
        
        now = datetime.now()
        sessions = self.get_user_sessions(user_id, status="completed")
        
        # Фильтруем по периоду
        filtered_sessions = []
        
        for session in sessions:
            started_at = datetime.fromisoformat(session["started_at"])
            
            if period == 'today':
                if started_at.date() == now.date():
                    filtered_sessions.append(session)
            elif period == 'week':
                week_ago = now - timedelta(days=7)
                if started_at >= week_ago:
                    filtered_sessions.append(session)
            else:  # all
                filtered_sessions.append(session)
        
        # Считаем статистику
        total_minutes = sum(session["duration_min"] for session in filtered_sessions)
        
        return {
            "session_count": len(filtered_sessions),
            "total_minutes": total_minutes,
            "sessions": filtered_sessions
        }