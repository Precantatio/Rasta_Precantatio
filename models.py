# Импорт нужных модулей
from dataclasses import dataclass # Библиотека с инструментами для классов
from datetime import datetime
from enum import Enum

# Перечисление для статусов сессии 
class SessionStatus(Enum):
    active = 'active'
    finish = 'completed' #Всё в этом классе константа 
    cancel = 'canceled'

# Класс для сессии фокуса
@dataclass 
class FocusSession:
    
        id: int = None 
        user_id: int = None
        started_at: datetime = None
        ended_at: datetime = None 
        planned_duration_min: int = 25
        actual_duration_min: int = 0
        status: SessionStatus = SessionStatus.active
    
# Метод для проверки активности 
def is_active(self) -> bool:
      return self.status == SessionStatus.active