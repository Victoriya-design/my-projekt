import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Всегда .env рядом с bot.py (не путать с automation/.env).
load_dotenv(Path(__file__).resolve().parent / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", r"D:\my-projekt")).resolve()
INBOX_DIR = PROJECT_ROOT / "inbox"
MEDIA_DIR = INBOX_DIR / "media"
CAPTURE_FILE = INBOX_DIR / "telegram-capture.md"


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
# Меньше «шума»: без строк про каждый HTTP-запрос к Telegram (httpx).
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


def ensure_paths() -> None:
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    if not CAPTURE_FILE.exists():
        CAPTURE_FILE.write_text("# Telegram Capture\n\n", encoding="utf-8")


def append_capture(text: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with CAPTURE_FILE.open("a", encoding="utf-8") as f:
        f.write(f"- [{now}] {text}\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Готово. Присылай текст, фото или голос. Я сохраню это в inbox проекта."
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.text:
        return

    append_capture(message.text.strip())
    await message.reply_text("Сохранила в inbox/telegram-capture.md")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.photo:
        return

    now = datetime.now()
    day_folder = MEDIA_DIR / now.strftime("%Y-%m-%d")
    day_folder.mkdir(parents=True, exist_ok=True)

    photo = message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_name = f"{now.strftime('%H%M%S')}_{photo.file_unique_id}.jpg"
    destination = day_folder / file_name
    await file.download_to_drive(destination)

    caption = message.caption.strip() if message.caption else "(без подписи)"
    append_capture(f"[PHOTO] {destination.as_posix()} | {caption}")
    await message.reply_text(f"Фото сохранено: {destination.as_posix()}")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message or not message.voice:
        return

    now = datetime.now()
    day_folder = MEDIA_DIR / now.strftime("%Y-%m-%d")
    day_folder.mkdir(parents=True, exist_ok=True)

    voice = message.voice
    file = await context.bot.get_file(voice.file_id)
    file_name = f"{now.strftime('%H%M%S')}_{voice.file_unique_id}.ogg"
    destination = day_folder / file_name
    await file.download_to_drive(destination)

    append_capture(f"[VOICE] {destination.as_posix()}")
    await message.reply_text(f"Голос сохранен: {destination.as_posix()}")


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is empty. Set it in .env file.")

    ensure_paths()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Python 3.12+ (в т.ч. 3.14): в главном потоке нет цикла по умолчанию,
    # а run_polling внутри вызывает asyncio.get_event_loop().
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.set_event_loop(asyncio.new_event_loop())

    logger.info("Telegram bot started.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
