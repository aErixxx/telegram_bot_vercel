import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message
from aiogram.filters import Command

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ดึง Bot Token จาก Environment Variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# สร้าง FastAPI app
app = FastAPI(title="Telegram Bot", version="1.0.0")

# สร้าง bot และ dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Command handlers
@dp.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command"""
    await message.reply(
        f"สวัสดี {message.from_user.first_name}! 👋\n"
        "ยินดีต้อนรับสู่บอทของเรา\n\n"
        "คำสั่งที่ใช้ได้:\n"
        "/start - เริ่มต้นใช้งาน\n"
        "/help - ดูความช่วยเหลือ\n"
        "/info - ข้อมูลเกี่ยวกับบอท"
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = """
🤖 **คำสั่งที่ใช้ได้:**

/start - เริ่มต้นใช้งานบอท
/help - แสดงความช่วยเหลือ
/info - ข้อมูลเกี่ยวกับบอท

📝 **วิธีใช้งาน:**
- ส่งข้อความมาได้เลย บอทจะตอบกลับ
- ใช้คำสั่งด้านบนเพื่อดูฟีเจอร์ต่างๆ

💡 **ติดต่อ:** @your_username
    """
    await message.reply(help_text, parse_mode="Markdown")

@dp.message(Command("info"))
async def info_command(message: Message):
    """Handle /info command"""
    info_text = """
ℹ️ **ข้อมูลบอท**

🔸 ชื่อ: Telegram Bot
🔸 เวอร์ชั่น: 1.0.0
🔸 พัฒนาด้วย: aiogram + FastAPI + Vercel
🔸 สถานะ: ออนไลน์ ✅

📊 **ข้อมูลผู้ใช้:**
- ชื่อ: {first_name}
- ID: {user_id}
- Username: @{username}
    """.format(
        first_name=message.from_user.first_name or "ไม่ระบุ",
        user_id=message.from_user.id,
        username=message.from_user.username or "ไม่ระบุ"
    )
    await message.reply(info_text)

# Handle ข้อความทั่วไป
@dp.message()
async def echo_message(message: Message):
    """Echo any message that's not a command"""
    if message.text:
        # Simple echo with some processing
        response = f"คุณส่งมาว่า: {message.text}\n\n"
        response += f"📝 ความยาวข้อความ: {len(message.text)} ตัวอักษร\n"
        response += f"⏰ เวลา: {message.date.strftime('%H:%M:%S')}"
        
        await message.reply(response)
    else:
        await message.reply("ขอโทษครับ ตอนนี้รองรับเฉพาะข้อความเท่านั้น")

# FastAPI Routes
@app.get("/")
async def root():
    """Get bot status"""
    return JSONResponse({
        "message": "🤖 Telegram Bot is running!",
        "status": "OK",
        "bot_info": {
            "name": "Telegram Bot",
            "version": "1.0.0",
            "framework": "aiogram + FastAPI + Vercel",
            "available_commands": ["/start", "/help", "/info"]
        }
    })

@app.post("/webhook")
async def webhook(request: Request):
    """Process Telegram webhook"""
    try:
        # Parse JSON body
        webhook_data = await request.json()
        logger.info(f"📨 Received webhook: {webhook_data}")
        
        # ตรวจสอบว่าเป็น Telegram update หรือไม่
        if 'update_id' not in webhook_data:
            logger.warning("⚠️ Invalid webhook data - missing update_id")
            raise HTTPException(status_code=400, detail="Invalid webhook data")
        
        # Create Update object
        update = Update(**webhook_data)
        
        # Process the update
        await dp.feed_update(bot, update)
        
        return JSONResponse({
            "ok": True,
            "update_id": webhook_data.get('update_id'),
            "processed": True
        })
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "bot_token_set": bool(BOT_TOKEN),
        "timestamp": "2024-06-24"
    })

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url.path)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Main handler function สำหรับ Vercel
handler = app
