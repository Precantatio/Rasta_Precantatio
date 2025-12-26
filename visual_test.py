# visual_test.py - ОЧЕНЬ ПРОСТОЙ ТЕСТ
import sys
import os

# Добавляем текущую папку в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Начинаем проверку...")

try:
    # Пробуем импортировать всё
    print("1. Импортируем модули...")
    from core.models import FocusSession
    from storage.repository import FocusRepository
    from core.service import FocusService
    print("   ✅ Все импорты успешны!")
    
    print("\n2. Создаём объекты...")
    # Тестируем
    service = FocusService()
    print("   ✅ Сервис создан")
    
    print("\n3. Делаем тестовый прогон...")
    result = service.start_session(777, 1)
    print(f"   Старт сессии: {result['message']}")
    
    status = service.get_status(777)
    print(f"   Статус: {status['message']}")
    
    result = service.stop_session(777)
    print(f"   Стоп сессии: {result['message']}")
    
    print("\n" + "🌈" * 20)
    print("ВСЁ РАБОТАЕТ ИДЕАЛЬНО!")
    print("🌈" * 20)
    
except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    print("\nВозможные проблемы:")
    print("1. Нет файлов core/models.py, storage/repository.py, core/service.py")
    print("2. Нет пустых файлов __init__.py в папках core/ и storage/")
    print("3. Запускаешь не из папки focus_bot/")
    