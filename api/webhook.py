import os
import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message
from aiogram.filters import Command
from command import router

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ดึง Bot Token จาก Environment Variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# สร้าง bot และ dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

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
    help_text = """🤖 คำสั่งที่ใช้ได้:

/start - เริ่มต้นใช้งานบอท
/help - แสดงความช่วยเหลือ
/info - ข้อมูลเกี่ยวกับบอท

📝 วิธีใช้งาน:
- ส่งข้อความมาได้เลย บอทจะตอบกลับ
- ใช้คำสั่งด้านบนเพื่อดูฟีเจอร์ต่างๆ

💡 ติดต่อ: @your_username"""
    
    # ใช้ HTML แทน Markdown และหลีกเลี่ยง special characters
    await message.answer(help_text)

@dp.message(Command("info"))
async def info_command(message: Message):
    """Handle /info command"""
    info_text = """ℹ️ ข้อมูลบอท

🔸 ชื่อ: Telegram Bot
🔸 เวอร์ชั่น: 1.0.0
🔸 พัฒนาด้วย: aiogram + Vercel
🔸 สถานะ: ออนไลน์ ✅

📊 ข้อมูลผู้ใช้:
- ชื่อ: {first_name}
- ID: {user_id}
- Username: @{username}""".format(
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
        
        await message.answer(response)
    else:
        await message.answer("ขอโทษครับ ตอนนี้รองรับเฉพาะข้อความเท่านั้น")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/" or path == "":
                # Root endpoint
                response_data = {
                    "message": "🤖 Telegram Bot is running!",
                    "status": "OK",
                    "bot_info": {
                        "name": "Telegram Bot",
                        "version": "1.0.0",
                        "framework": "aiogram + Vercel",
                        "available_commands": ["/start", "/help", "/info"]
                    }
                }
                self._send_json_response(200, response_data)
                
            elif path == "/health":
                # Health check endpoint
                response_data = {
                    "status": "healthy",
                    "bot_token_set": bool(BOT_TOKEN),
                    "timestamp": datetime.now().isoformat()
                }
                self._send_json_response(200, response_data)
                
            else:
                # 404 for other paths
                self._send_json_response(404, {
                    "error": "Endpoint not found",
                    "path": path
                })
                
        except Exception as e:
            logger.error(f"❌ Error in GET request: {e}")
            self._send_json_response(500, {
                "error": "Internal server error",
                "detail": str(e)
            })

    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            if path == "/webhook":
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # Parse JSON
                webhook_data = json.loads(post_data.decode('utf-8'))
                logger.info(f"📨 Received webhook: {webhook_data}")
                
                # ตรวจสอบว่าเป็น Telegram update หรือไม่
                if 'update_id' not in webhook_data:
                    logger.warning("⚠️ Invalid webhook data - missing update_id")
                    self._send_json_response(400, {
                        "error": "Invalid webhook data"
                    })
                    return
                
                # Process webhook with proper event loop handling
                import asyncio
                try:
                    # Create new event loop for serverless environment
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Run the webhook processing
                    loop.run_until_complete(self._process_webhook(webhook_data))
                    
                except Exception as e:
                    logger.error(f"❌ Error in async processing: {e}")
                finally:
                    # Clean up the loop properly
                    try:
                        loop.close()
                    except:
                        pass
                
                # Send success response
                self._send_json_response(200, {
                    "ok": True,
                    "update_id": webhook_data.get('update_id'),
                    "processed": True
                })
                
            else:
                self._send_json_response(404, {
                    "error": "Endpoint not found",
                    "path": path
                })
                
        except json.JSONDecodeError:
            self._send_json_response(400, {
                "error": "Invalid JSON in request body"
            })
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            self._send_json_response(500, {
                "error": "Internal server error",
                "detail": str(e)
            })

    async def _process_webhook(self, webhook_data):
        """Process Telegram webhook data"""
        try:
            # Create Update object
            update = Update(**webhook_data)
            
            # Create a fresh bot instance for this request
            bot_instance = Bot(token=BOT_TOKEN)
            
            # Process the update with proper session management
            try:
                await dp.feed_update(bot_instance, update)
            finally:
                # Close bot session properly
                await bot_instance.session.close()
            
        except Exception as e:
            logger.error(f"❌ Error processing update: {e}")
            raise

    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Override log message to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")
