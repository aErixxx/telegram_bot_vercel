import os
import logging
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Update
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # Optional: Set in .env

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in environment variables")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

app = FastAPI()

# ---------------- Handlers -----------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("สวัสดี! ยินดีต้อนรับสู่บอทเทเลแกรม")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("นี่คือบอทตัวอย่าง ใช้งานง่าย!")

@dp.message()
async def echo_message(message: types.Message):
    await message.answer(f"คุณส่งข้อความว่า:\n\n{message.text}")

# ------------------------------------------

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        # Validate webhook secret (optional)
        if WEBHOOK_SECRET:
            secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret != WEBHOOK_SECRET:
                raise HTTPException(status_code=403, detail="Invalid webhook secret")

        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return {"error": str(e)}