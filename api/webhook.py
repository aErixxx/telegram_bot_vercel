import os
import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Update, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CallbackQueryFilter

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ดึง Bot Token จาก Environment Variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# สร้าง bot และ dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Callback query handler สำหรับปุ่ม OK และ Cancel
@router.callback_query(CallbackQueryFilter(callback_data=["btn_ok", "btn_cancel"]))
async def handle_button_click(callback_query):
    try:
        if callback_query.data == "btn_ok":
            await callback_query.message.answer("ได้รับการยืนยัน OK", reply_to_message_id=callback_query.message.message_id)
        elif callback_query.data == "btn_cancel":
            await callback_query.message.answer("ยกเลิกเรียบร้อย", reply_to_message_id=callback_query.message.message_id)
        await callback_query.answer()  # หยุดวงกลม loading
        logger.info(f"Processed callback query: {callback_query.data}")
    except Exception as e:
        logger.error(f"Error processing callback query: {str(e)}")

# Command handler (ตัวอย่างสำหรับ /start)
@router.message(Command("start"))
async def start_command(message):
    await message.answer("สวัสดี! Bot พร้อมใช้งานแล้ว")
    logger.info(f"Processed /start command from chat {message.chat.id}")

# รวม router เข้ากับ dispatcher
dp.include_router(router)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == "/" or path == "":
                response_data = {
                    "message": "🤖 Telegram Bot Vercel is running!",
                    "status": "OK",
                    "bot_info": {
                        "name": "aErix Assistants Bot",
                        "version": "1.0.0",
                        "framework": "aiogram + Vercel"
                    }
                }
                self._send_json_response(200, response_data)
                
            elif path == "/status":
                response_data = {
                    "status": "Ok",
                    "bot_token_set": bool(BOT_TOKEN),
                    "timestamp": datetime.now().isoformat()
                }
                self._send_json_response(200, response_data)
                
            else:
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
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                webhook_data = json.loads(post_data.decode('utf-8'))
                logger.info(f"📨 Received webhook: {webhook_data}")
                
                if 'update_id' not in webhook_data:
                    logger.warning("⚠️ Invalid webhook data - missing update_id")
                    self._send_json_response(400, {
                        "error": "Invalid webhook data"
                    })
                    return
                
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    update = Update(**webhook_data)
                    bot_instance = Bot(token=BOT_TOKEN)
                    try:
                        await dp.feed_update(bot_instance, update)
                    finally:
                        await bot_instance.session.close()
                except Exception as e:
                    logger.error(f"❌ Error in async processing: {e}")
                finally:
                    loop.close()
                
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
            
    def do_HEAD(self):
        path = self.path
        if path in ["/", "/status"]:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        
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
