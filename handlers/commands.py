from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

async def cmd_start(message: Message):
    """Handle /start command"""
    user_name = message.from_user.first_name or "เพื่อน"
    welcome_text = f"""
🤖 <b>สวัสดี {user_name}!</b>

ยินดีต้อนรับสู่บอทเทเลแกรม

📋 <b>คำสั่งที่ใช้ได้:</b>
/start - เริ่มต้นใช้งาน
/help - ดูวิธีใช้งาน
/about - เกี่ยวกับบอท

💬 หรือส่งข้อความมาคุยกับบอทได้เลย!
    """
    await message.answer(welcome_text)

async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = """
🆘 <b>วิธีใช้งานบอท</b>

📌 <b>คำสั่งพื้นฐาน:</b>
- /start - เริ่มต้นใช้งาน
- /help - แสดงข้อมูลช่วยเหลือ
- /about - ข้อมูลเกี่ยวกับบอท

💭 <b>การใช้งาน:</b>
- ส่งข้อความใดๆ และบอทจะตอบกลับ
- บอทสามารถตอบข้อความภาษาไทยได้

❓ หากมีปัญหาการใช้งาน ติดต่อผู้พัฒนาได้
    """
    await message.answer(help_text)

async def cmd_about(message: Message):
    """Handle /about command"""
    about_text = """
ℹ️ <b>เกี่ยวกับบอท</b>

🤖 <b>ชื่อ:</b> Telegram Bot Example
🚀 <b>Platform:</b> Vercel + aiogram
💻 <b>Version:</b> 1.0.0

🛠️ <b>เทคโนโลยีที่ใช้:</b>
- Python 3.13
- aiogram 3.x
- FastAPI
- Vercel Serverless

📅 สร้างเมื่อ: 2025
👨‍💻 <b>Developer:</b> Your Name
    """
    await message.answer(about_text)

async def echo_message(message: Message):
    """Echo user messages with some processing"""
    if message.text:
        response_text = f"""
💬 <b>คุณส่งข้อความว่า:</b>
"{message.text}"

📊 <b>ข้อมูลเพิ่มเติม:</b>
- ความยาว: {len(message.text)} ตัวอักษร
- จำนวนคำ: {len(message.text.split())} คำ
- เวลา: {message.date.strftime('%H:%M:%S')}

🤖 ขอบคุณที่ใช้บริการ!
        """
        await message.answer(response_text)
    else:
        await message.answer("🤔 ขออภัย ฉันไม่เข้าใจข้อความนี้")

def register_handlers(dp: Dispatcher):
    """Register all message handlers"""
    # Command handlers
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_about, Command("about"))
    
    # Text message handler
    dp.message.register(echo_message, F.text)