# Telegram -> Cursor Inbox

Этот бот принимает сообщения из Telegram и сохраняет их в проект:

- текст -> `inbox/telegram-capture.md`
- фото -> `inbox/media/YYYY-MM-DD/*.jpg`
- голос -> `inbox/media/YYYY-MM-DD/*.ogg`

## 1) Создать бота в Telegram

1. Откройте `@BotFather` в Telegram.
2. Отправьте `/newbot`.
3. Задайте имя и username.
4. Скопируйте токен бота.

## 2) Подготовить файлы

1. Откройте папку `automation/telegram-bot`.
2. Скопируйте `.env.example` в `.env`.
3. В `.env` вставьте токен:

```env
TELEGRAM_BOT_TOKEN=ваш_токен
PROJECT_ROOT=D:\my-projekt
```

## 3) Установить зависимости

```powershell
cd D:\my-projekt\automation\telegram-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 4) Запустить бота

```powershell
python bot.py
```

Если все ок, увидите в консоли `Telegram bot started.`

## 5) Проверка

1. Напишите боту `/start`.
2. Отправьте текст "проверка".
3. Проверьте файл `inbox/telegram-capture.md`.

## 6) Как работать дальше в Cursor

Когда накидаете мысли в Telegram, в чате Cursor пишите:

`Разложи inbox/telegram-capture.md по папкам и обнови NEXT.md.`

## Опционально: автозапуск после перезагрузки

Можно добавить запуск через Планировщик задач Windows (Task Scheduler), чтобы бот поднимался автоматически.
