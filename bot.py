import os
import subprocess
import asyncio # برای اجرای غیرهمزمان (Async) دستورات سیستمی
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

# تنظیمات ربات
# ----------------------------------------------------------------------

# **مهم:** جایگزین کردن مقادیر زیر با اطلاعات واقعی خودتان
API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '8189638115:AAEYMDvummCXAPgdpavZbYHa3YuXpOzkRBY'
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه

bot = Client("watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# مسیر فایل واترمارک (باید در کنار bot.py باشد)
WATERMARK_FILE = "logo.png"

# مسیرهای موقت برای ویدیوها
INPUT_VIDEO_PATH = "input_video_{}.mp4"
OUTPUT_VIDEO_PATH = "output_video_{}.mp4"

# ----------------------------------------------------------------------
# هندلرهای ربات
# ----------------------------------------------------------------------

@bot.on_message(filters.command("start"))
async def start(client, message):
    """هندلر دستور /start"""
    await message.reply_text("سلام! من ربات واترمارک‌زن تو هستم. یک ویدیو برای من بفرست! 🚀")


@bot.on_message(filters.video & filters.private)
async def process_video(client: Client, message: Message):
    """هندلر برای پردازش ویدیوهای دریافتی و اضافه کردن واترمارک"""
    
    # ایجاد یک شناسه منحصر به فرد برای نامگذاری فایل‌ها (برای جلوگیری از تداخل)
    # از chat_id به عنوان بخشی از نام فایل استفاده می‌کنیم
    unique_id = message.chat.id
    input_path = INPUT_VIDEO_PATH.format(unique_id)
    output_path = OUTPUT_VIDEO_PATH.format(unique_id)
    
    # ۱. پیام در حال پردازش را ارسال کنید
    processing_msg = await message.reply_text("در حال دانلود ویدیو...")

    try:
        # ۲. ویدیوی ارسالی را دانلود کنید
        # از client.download_media برای دریافت فایل استفاده می‌کنیم
        await message.download(file_name=input_path)
        
        await processing_msg.edit_text("دانلود با موفقیت انجام شد. در حال اضافه کردن واترمارک... ⏳")

        # ۳. دستور FFmpeg برای اضافه کردن واترمارک
        # این دستور لوگو را در گوشه پایین سمت راست قرار می‌دهد
        ffmpeg_command = [
            "ffmpeg",
            "-i", input_path,             # ورودی ویدیو (0:v)
            "-i", WATERMARK_FILE,         # ورودی واترمارک (1:v)
            "-filter_complex",
            # فیلتر overlay: لوگو را 10 پیکسل از راست و پایین قرار می‌دهد
            "[0:v][1:v]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]",
            "-map", "[out]",
            
            # تنظیمات انکودر برای سازگاری بهتر و کاهش حجم
            "-c:v", "libx264",       # انکودر ویدیویی (باید در داکر نصب شود)
            "-crf", "23",            # کیفیت خروجی (23 کیفیت خوبی است)
            "-preset", "veryfast",   # سرعت انکد
            
            "-map", "0:a?",          # کپی کردن استریم صوتی اگر وجود داشته باشد (اختیاری)
            "-c:a", "copy",
            output_path              # خروجی ویدیو
        ]

        # ۴. اجرای دستور FFmpeg
        # استفاده از asyncio.create_subprocess_exec برای اجرای غیرهمزمان (Async)
        process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            # نمایش 500 کاراکتر اول خطا در صورت ناموفق بودن FFmpeg
            await processing_msg.edit_text(
                f"❌ خطایی در اضافه کردن واترمارک رخ داد.\n\n**خطای FFmpeg:**\n`{stderr.decode()[:500]}`"
            )
            return

        await processing_msg.edit_text("واترمارک با موفقیت اضافه شد. در حال آپلود... ⬆️")

        # ۵. ارسال ویدیوی خروجی
        await client.send_video(
            chat_id=message.chat.id,
            video=output_path,
            caption="✅ اینم ویدیوی شما با واترمارک! @YourBotUsername"
        )

        await processing_msg.delete() # حذف پیام در حال پردازش

    except MessageNotModified:
        # در صورتیکه پیام در حال ویرایش تغییر نکرده باشد، از خطا صرفنظر می‌کنیم
        pass
    except Exception as e:
        # مدیریت خطاهای کلی
        error_message = f"❌ یک خطای غیرمنتظره رخ داد: `{e}`"
        await client.send_message(message.chat.id, error_message)

    finally:
        # ۶. حذف فایل‌های موقت
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
# ----------------------------------------------------------------------
# اجرای ربات
# ----------------------------------------------------------------------
if __name__ == "__main__":
    bot.run()
