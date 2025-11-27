#!/usr/bin/env python3
"""
Простой скрипт для запуска FastAPI сервера
"""
import os
import sys
import subprocess

def check_python():
    """Проверка наличия Python"""
    # Пробуем прямой путь к Python 3.13
    python_path = r"C:\Program Files\Python313\python.exe"
    if os.path.exists(python_path):
        return python_path

    # Пробуем системные команды
    commands = ['python', 'python3', 'py']
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    return None

def install_dependencies():
    """Установка зависимостей"""
    python_cmd = check_python()
    if not python_cmd:
        print("Python не найден в системе!")
        return False

    print(f"Найден Python: {python_cmd}")
    try:
        print("Установка зависимостей...")
        result = subprocess.run([python_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("Зависимости успешно установлены!")
            return True
        else:
            print(f"Ошибка установки зависимостей: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("Установка зависимостей превысила время ожидания")
        return False
    except Exception as e:
        print(f"Ошибка при установке зависимостей: {e}")
        return False

def start_server():
    """Запуск сервера"""
    python_cmd = check_python()
    if not python_cmd:
        print("Не удалось найти Python!")
        return

    print("Запуск FastAPI сервера...")
    try:
        # Запускаем сервер в фоновом режиме
        subprocess.run([python_cmd, 'main.py'], cwd=os.getcwd())
    except KeyboardInterrupt:
        print("\nСервер остановлен пользователем")
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    print("=== Запуск News API сервера ===")

    # Проверка наличия .env файла
    if not os.path.exists('.env'):
        print("Создание .env файла...")
        with open('.env', 'w') as f:
            f.write('DATABASE_URL=postgresql://user:password@localhost:5432/news_db')

    # Установка зависимостей
    if not install_dependencies():
        print("Не удалось установить зависимости. Попробуйте установить их вручную:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Запуск сервера
    start_server()
