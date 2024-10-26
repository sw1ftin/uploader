#!/bin/bash

# Активация виртуального окружения
source venv/bin/activate

# Установка переменной окружения PORT
export PORT=5959

# Запуск приложения
python app.py