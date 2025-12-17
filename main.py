from focus_service import FocusService

def main():
    print("Начинаем тест")
    
    service = FocusService()
    user_id = 12345
    
    print("1. Создаем сессию на 2 минуты")
    result = service.start_session(user_id, 2)
    print(result)
    
    print("\n2. Смотрим статус")
    status = service.get_status(user_id)
    print(status)
    
    print("\n3. Пытаемся создать вторую сессию")
    result2 = service.start_session(user_id, 10)
    print(result2)
    
    print("\n4. Останавливаем сессию")
    stop_result = service.stop_session(user_id)
    print(stop_result)
    
    print("\n5. Снова смотрим статус")
    final_status = service.get_status(user_id)
    print(final_status)
    
    print("\n6. Смотрим статистику")
    stats = service.get_stats(user_id, 'today')
    print(stats)

if __name__ == "__main__":
    main()