# Terminal File Sharing

Terminal File Sharing - это веб-приложение для обмена файлами в стиле терминала, разработанное с использованием Flask и Telegram Bot API.

## Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/your-username/terminal-file-sharing.git
   cd terminal-file-sharing
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```
   python -m venv venv
   source venv/bin/activate  # Для Linux/macOS
   venv\Scripts\activate  # Для Windows
   ```

3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные окружения:
   ```
   SECRET_KEY=your_secret_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

   Для генерации SECRET_KEY используйте скрипт `generate_secret.py`:
   ```
   python generate_secret.py
   ```

   Для получения TELEGRAM_CHAT_ID используйте скрипт `get_telegram_chat_id.py`:
   ```
   python get_telegram_chat_id.py
   ```

## Запуск

Для запуска приложения выполните:
```
python app.py
```

Приложение будет доступно по адресу `http://localhost:5000`.

## Использование API

### Регистрация пользователя

- URL: `/register`
- Метод: POST
- Данные:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- Ответ:
  ```json
  {
    "message": "Аккаунт успешно создан!"
  }
  ```

### Авторизация

- URL: `/login`
- Метод: POST
- Данные:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- Ответ:
  ```json
  {
    "message": "Успешная авторизация"
  }
  ```

### Загрузка файла

- URL: `/upload`
- Метод: POST
- Заголовки: `Content-Type: multipart/form-data`
- Данные: `file: (binary)`
- Ответ:
  ```json
  {
    "success": true,
    "unique_link": "abcdef",
    "original_filename": "example.txt"
  }
  ```

### Скачивание файла

- URL: `/<unique_link>`
- Метод: GET
- Ответ: Файл для скачивания

### Удаление файла

- URL: `/delete_file/<file_id>`
- Метод: POST
- Ответ: Перенаправление на страницу панели управления

## Развертывание

Для развертывания приложения на сервере выполните следующие шаги:

1. Настройте веб-сервер (например, Nginx) для проксирования запросов к Flask-приложению.

2. Настройте WSGI-сервер (например, Gunicorn) для запуска Flask-приложения.

3. Настройте SSL-сертификат для безопасного соединения.

4. Настройте Telegram Bot и получите необходимые токены.

5. Установите зависимости и настройте переменные окружения на сервере.

6. Запустите приложение с помощью WSGI-сервера.

Подробные инструкции по развертыванию зависят от выбранного хостинга и конфигурации сервера.

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле LICENSE.
