# core/service.py
from datetime import datetime, timedelta
from storage.repository import FocusRepository
from core.models import FocusSession


class FocusService:
    def __init__(self, repository=None):
        self.repo = repository or FocusRepository()
    
    def start_session(self, user_id, minutes=25):
        # Проверяем активную сессию
        active = self.repo.get_active_session(user_id)
        if active:
            return {
                "success": False,
                "error": "У вас уже есть активная сессия"
            }
        
        # Создаем новую
        session = self.repo.create_session(user_id, minutes)
        
        # Вычисляем время окончания
        end_time = session.started_at + timedelta(minutes=minutes)
        
        return {
            "success": True,
            "session": session,
            "end_time": end_time,
            "message": f"Сессия на {minutes} минут началась!"
        }
    
    def stop_session(self, user_id, cancel=False):
        session = self.repo.get_active_session(user_id)
        if not session:
            return {
                "success": False,
                "error": "Нет активной сессии"
            }
        
        if cancel:
            self.repo.cancel_session(session.id)
            message = "Сессия отменена"
        else:
            self.repo.complete_session(session.id)
            message = "Сессия завершена успешно!"
        
        return {
            "success": True,
            "message": message,
            "session": session
        }
    
    def get_status(self, user_id):
        session = self.repo.get_active_session(user_id)
        if not session:
            return {
                "has_active": False,
                "message": "Нет активной сессии"
            }
        
        # Вычисляем оставшееся время
        elapsed = datetime.now() - session.started_at
        remaining_seconds = session.planned_duration_min * 60 - elapsed.total_seconds()
        remaining_minutes = max(0, int(remaining_seconds // 60))
        
        return {
            "has_active": True,
            "session": session,
            "remaining_minutes": remaining_minutes,
            "message": f"Осталось: {remaining_minutes} мин."
        }
    
    def get_stats(self, user_id, period="today"):
        stats = self.repo.get_user_stats(user_id, period)
        
        if period == "today":
            period_text = "сегодня"
        elif period == "week":
            period_text = "за неделю"
        else:
            period_text = f"за период {period}"
        
        return {
            "period": period_text,
            "stats": stats,
            "message": f"Статистика {period_text}: {stats['sessions']} сессий, {stats['total_minutes']} минут"
        }


