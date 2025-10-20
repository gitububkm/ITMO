#!/usr/bin/env python3
"""
Скрипт для тестирования API эндпоинтов
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_root():
    """Тестирование корневого эндпоинта"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(" Корневой эндпоинт работает")
            print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f" Корневой эндпоинт вернул статус {response.status_code}")
            return False
    except Exception as e:
        print(f" Ошибка при обращении к корневому эндпоинту: {e}")
        return False

def test_docs():
    """Тестирование Swagger документации"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(" Swagger UI доступен")
            return True
        else:
            print(f" Swagger UI вернул статус {response.status_code}")
            return False
    except Exception as e:
        print(f" Ошибка при обращении к Swagger UI: {e}")
        return False

def test_openapi():
    """Тестирование OpenAPI схемы"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            print(" OpenAPI схема доступна")
            data = response.json()
            print(f"   Название API: {data.get('info', {}).get('title', 'N/A')}")
            print(f"   Версия: {data.get('info', {}).get('version', 'N/A')}")
            return True
        else:
            print(f" OpenAPI схема вернула статус {response.status_code}")
            return False
    except Exception as e:
        print(f" Ошибка при обращении к OpenAPI схеме: {e}")
        return False

def test_users():
    """Тестирование эндпоинтов пользователей"""
    try:
        # Получение всех пользователей
        response = requests.get(f"{BASE_URL}/users/")
        if response.status_code == 200:
            print(" Получение пользователей работает")
            users = response.json()
            print(f"   Количество пользователей: {len(users)}")
            return True
        else:
            print(f" Получение пользователей вернуло статус {response.status_code}")
            return False
    except Exception as e:
        print(f" Ошибка при обращении к пользователям: {e}")
        return False

def test_news():
    """Тестирование эндпоинтов новостей"""
    try:
        # Получение всех новостей
        response = requests.get(f"{BASE_URL}/news/")
        if response.status_code == 200:
            print(" Получение новостей работает")
            news = response.json()
            print(f"   Количество новостей: {len(news)}")
            return True
        else:
            print(f" Получение новостей вернуло статус {response.status_code}")
            return False
    except Exception as e:
        print(f" Ошибка при обращении к новостям: {e}")
        return False

def test_comments():
    """Тестирование эндпоинтов комментариев"""
    try:
        # Получение всех комментариев
        response = requests.get(f"{BASE_URL}/comments/")
        if response.status_code == 200:
            print(" Получение комментариев работает")
            comments = response.json()
            print(f"   Количество комментариев: {len(comments)}")
            return True
        else:
            print(f" Получение комментариев вернуло статус {response.status_code}")
            return False
    except Exception as e:
        print(f" Ошибка при обращении к комментариям: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("=== Тестирование News API ===")
    print(f"Базовый URL: {BASE_URL}")
    print()

    tests = [
        ("Корневой эндпоинт", test_root),
        ("Swagger UI", test_docs),
        ("OpenAPI схема", test_openapi),
        ("Пользователи", test_users),
        ("Новости", test_news),
        ("Комментарии", test_comments),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"Тестирование: {test_name}")
        success = test_func()
        results.append((test_name, success))
        print()
        time.sleep(1)  # Небольшая пауза между тестами

    # Итоги
    print("=== ИТОГИ ТЕСТИРОВАНИЯ ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = " ПРОЙДЕН" if success else " ПРОВАЛЕН"
        print(f"{status}: {test_name}")

    print(f"\nОбщий результат: {passed}/{total} тестов пройдено")

    if passed == total:
        print(" Все тесты прошли успешно!")
    else:
        print("  Некоторые тесты провалились. Проверьте настройки сервера.")

if __name__ == "__main__":
    main()
