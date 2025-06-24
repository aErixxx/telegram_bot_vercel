from aiogram import Router, types
from aiogram.types import Message
import logging

logger = logging.getLogger(__name__)
router = Router()

admin_chat_id = os.getenv("ADMIN_ID")# เปลี่ยนเป็น chat_id ของแอดมินจริง ๆ ของคุณ

# Command handlers
@router.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command"""
    await message.reply(
        f"สวัสดี {message.from_user.first_name}! 👋\n"
        "ยินดีต้อนรับสู่บอทของเรา\n\n"
        "คำสั่งที่ใช้ได้:\n"
        "/start - เริ่มต้นใช้งาน\n"
        "/help - ดูความช่วยเหลือ\n"
        "/info - ข้อมูลเกี่ยวกับบอท\n\n"
        "ฟีเจอร์:\n"
        "- ตอบกลับข้อความ (Echo) ที่ผู้ใช้ส่งมา\n"
        "- รองรับการรับและจัดการสื่อหลายประเภท เช่น รูปภาพ, ไฟล์เอกสาร, วิดีโอ, เสียง และข้อความเสียง\n"
        "- ติดตามการตอบกลับ (reply) ของผู้ใช้ "\n"
    )
    
@router.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = """🤖 คำสั่งที่ใช้ได้:

/start - เริ่มต้นใช้งานบอท
/help - แสดงความช่วยเหลือ
/info - ข้อมูลเกี่ยวกับบอท

📝 วิธีใช้งาน:
- ส่งข้อความมาได้เลย บอทจะตอบกลับ
- ใช้คำสั่งด้านบนเพื่อดูฟีเจอร์ต่างๆ
"""
    # ใช้ HTML แทน Markdown และหลีกเลี่ยง special characters
    await message.answer(help_text)

@router.message(Command("info"))
async def info_command(message: Message):
    """Handle /info command"""
    info_text = """ℹ️ ข้อมูลบอท

🔸 ชื่อ: aErix Assistants Bot
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
    
@router.message()
async def echo_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    if message.reply_to_message:
        replied_message = message.reply_to_message
        replied_caption_text = replied_message.caption or ""

        type_checks = [
            ("ข้อความ", lambda m: bool(m.text), lambda m: m.text),
            ("รูปภาพ", lambda m: bool(m.photo), lambda m: "รูปภาพ"),
            ("ไฟล์", lambda m: bool(m.document), lambda m: f"ไฟล์: {m.document.file_name or 'ไฟล์ไม่ทราบชื่อ'}"),
            ("วิดีโอ", lambda m: bool(m.video), lambda m: "วิดีโอ"),
            ("เสียง", lambda m: bool(m.audio), lambda m: "เสียง"),
            ("ข้อความเสียง", lambda m: bool(m.voice), lambda m: "ข้อความเสียง"),
            ("สติกเกอร์", lambda m: bool(m.sticker), lambda m: "สติกเกอร์"),
        ]

        replied_type = "ไม่สามารถระบุประเภทได้"
        replied_filename = "ไม่มีชื่อไฟล์หรือข้อมูลที่รู้จัก"

        for t, check, get_content in type_checks:
            if check(replied_message):
                replied_type = t
                replied_filename = get_content(replied_message)
                break

        if replied_caption_text:
            replied_content = f"{replied_filename}:\n\n{replied_caption_text}"
        else:
            replied_content = replied_filename

        logger.info(f"ได้รับ reply จาก {username} (ID: {user_id}): {message.text} -> ตอบกลับ{replied_type}: {replied_content}")

        if message.text and message.text.lower() == "ok":
            await message.answer(f"✅ แจ้งเตือนเรียบร้อยแล้ว \n\n {replied_filename[:80]}")
            try:
                notification_text = (
                    f"🧑‍💻 ผู้ใช้ {username} (ID: {user_id}) Reply\n\n"
                    f"สถานะ: ✅ OK\n<pre>{replied_content[:200]}</pre>"
                )
                await message.bot.send_message(chat_id=admin_chat_id, text=notification_text, parse_mode="HTML")
            except Exception as e:
                logger.error(f"เกิดข้อผิดพลาดในการส่งการแจ้งเตือน reply ไปยัง admin: {e}")
        else:
            try:
                notification_text = f"\n-----------------------------------------\n"
                notification_text += f"🧑‍💻 ผู้ใช้ {username} (ID: {user_id}) Reply Message\n\n"
                notification_text += f"✏️ มีแก้ไข: {replied_content[:200]}\n\n"
                notification_text += f"📝 ข้อความ: \n\n<pre>{message.text}</pre>"

                await message.answer(f"📌รับทราบครับ จะรีบแก้ไขทันที!\n\n{replied_content}")

                if replied_message.text:
                    await message.answer(f"<pre>{replied_message.text}</pre>", parse_mode="HTML")
                elif replied_message.photo:
                    await message.answer_photo(replied_message.photo[-1].file_id, caption=notification_text)
                elif replied_message.document:
                    await message.answer_document(replied_message.document.file_id, caption=notification_text)
                elif replied_message.video:
                    await message.answer_video(replied_message.video.file_id, caption=notification_text)
                elif replied_message.audio:
                    await message.answer_audio(replied_message.audio.file_id, caption=notification_text)
                elif replied_message.voice:
                    await message.answer_voice(replied_message.voice.file_id, caption=notification_text)
                elif replied_message.sticker:
                    await message.answer_sticker(replied_message.sticker.file_id)
                else:
                    await message.answer("ไม่สามารถส่งเนื้อหาที่คุณ reply กลับไปได้")
            except Exception as e:
                logger.error(f"เกิดข้อผิดพลาดในการส่งการแจ้งเตือน reply ไปยัง admin: {e}")

    elif message.document or message.photo or message.video:
        if message.document:
            await message.bot.send_document(
                chat_id=admin_chat_id,
                document=message.document.file_id,
                caption=f"📁 ผู้ใช้ {username} (ID: {user_id}) ส่งไฟล์เอกสาร:\n {message.document.file_name or 'ไม่ทราบชื่อไฟล์'}"
            )
            await message.answer(f"📎ได้รับ {message.document.file_name} เรียบร้อยแล้ว")

        elif message.photo:
            photo_file_id = message.photo[-1].file_id
            photo_filename = f"photo_{photo_file_id[:10]}.jpg"
            caption = message.caption or ""
            combined_caption = f"📁 ผู้ใช้ {username} (ID: {user_id})\nส่งรูปภาพ: {photo_filename}"
            if caption:
                combined_caption += f"\n📝 คำอธิบาย:\n {caption}"
            await message.bot.send_photo(chat_id=admin_chat_id, photo=photo_file_id, caption=combined_caption)
            await message.answer(f"📎ไฟล์: {photo_filename}\nผลการส่ง: OK" + (f" ({caption})" if caption else ""))

        elif message.video:
            video_file_id = message.video.file_id
            video_filename = getattr(message.video, "file_name", None) or f"video_{video_file_id[:10]}.mp4"
            await message.bot.send_video(
                chat_id=admin_chat_id,
                video=video_file_id,
                caption=f"📁 ผู้ใช้ {username} (ID: {user_id}) ส่งวิดีโอ: {video_filename}"
            )
            await message.answer(f"📎 ได้รับไฟล์: {video_filename} เรียบร้อยแล้ว")

    elif message.text and message.text.lower() == "ok":
        await message.answer("✅ รับทราบแล้ว! ขอบคุณสำหรับการยืนยัน")
        try:
            await message.bot.send_message(
                chat_id=admin_chat_id,
                text=f"📝 ผู้ใช้ {username} (ID: {user_id}) \n ส่งด้วยข้อความธรรมดา: {message.text}"
            )
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการส่งการแจ้งเตือนไปยัง admin: {e}")

    else:
        if message.text:
            await message.answer(f"ข้อความของคุณ: {message.text}")
        else:
            await message.answer("ได้รับข้อความของคุณแล้ว!")

