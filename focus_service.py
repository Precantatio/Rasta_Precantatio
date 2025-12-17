from datetime import datetime, timedelta
from typing import Dict, Any
from storage import JSONStorage

class FocusService: #Это мозг приложения 
    def __init__(self): # При создании объекта FocusService создаем объект JSONStorage
        self.storage = JSONStorage()
    
    def start_session(self, user_id: int, minutes: int = 25) -> Dict[str, Any]: #Сессия фокуса, пример 25мин
        active = self.storage.get_active_session(user_id)
        if active:
            return {
                'success': False,
                'error': 'Уже есть активная сессия',
                'active_session': active
            }
        
        session_id = self.storage.create_session(user_id, minutes)
        ends_at = datetime.now() + timedelta(minutes=minutes)
        
        return {
            'success': True,
            'message': f'Сессия на {minutes} минут начата!',
            'session_id': session_id,
            'ends_at': ends_at,
            'duration': minutes
        }
    
    def stop_session(self, user_id: int) -> Dict[str, Any]: 
        active = self.storage.get_active_session(user_id)
        if not active:
            return {
                'success': False,
                'error': 'Нет активной сессии'
            }
        
        self.storage.update_session(active["id"], {"status": "canceled"})
        
        return {
            'success': True,
            'message': 'Сессия остановлена',
            'session_id': active["id"],
            'duration': active["duration_min"]
        }
    
    def complete_session(self, session_id: int):
        self.storage.update_session(session_id, {"status": "completed"})
    
    def get_status(self, user_id: int) -> Dict[str, Any]: #Это статус текущей сессии 
        active = self.storage.get_active_session(user_id) #Это активная сессия "получаем"
        if not active:
            return {
                'has_active': False,
                'message': 'Нет активной сессии'
            }
        
        started = datetime.fromisoformat(active["started_at"]) # Строку с датой начала в объект datatime 
        duration = active["duration_min"]
        ends_at = started + timedelta(minutes=duration)
        remaining = ends_at - datetime.now()
        
        if remaining.total_seconds() <= 0: #Проверяем не истекло ли время 
            self.complete_session(active["id"])
            return {
                'has_active': False,
                'message': 'Сессия завершена!'
            } # завершаем сессию и возвращаем сообщение p.s Я постараюсь поменьше комментариев писать если понятно и так что к чему.
        
        remaining_minutes = int(remaining.total_seconds() // 60)
        remaining_seconds = int(remaining.total_seconds() % 60)
        
        return {
            'has_active': True,
            'message': f'Осталось: {remaining_minutes} мин {remaining_seconds} сек',
            'ends_at': ends_at.isoformat(),
            'remaining_minutes': remaining_minutes,
            'session_id': active["id"]
        } #Это возврат информации о текушей сессии
    
    def get_stats(self, user_id: int, period: str = 'today') -> Dict[str, Any]:
        stats = self.storage.get_user_stats(user_id, period)
        
        return {
            'period': period,
            'session_count': stats['session_count'],
            'total_minutes': stats['total_minutes'],
            'message': f'За {period}: {stats["session_count"]} сессий, {stats["total_minutes"]} минут',
            'sessions': stats['sessions']
        }
    
    def check_and_complete_expired(self):
        data = self.storage._load_data()
        for session in data["sessions"]:
            if session["status"] == "active":
                started = datetime.fromisoformat(session["started_at"])
                ends_at = started + timedelta(minutes=session["duration_min"])
                if datetime.now() > ends_at:
                    self.complete_session(session["id"])