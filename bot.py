import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# تنظیمات ربات
API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '8189638115:AAEYMDvummCXAPgdpavZbYHa3YuXpOzkRBY'
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه

bot = Client("watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# مسیر فایل واترمارک
WATERMARK_FILE = "logo.png"

# مسیرهای موقت برای ویدیوها
INPUT_VIDEO_PATH = "input_video.mp4"
OUTPUT_VIDEO_PATH = "output_video.mp4"

# ----------------------------------------------------------------------

# هندلر دستور /start
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("سلام! من ربات ساده‌ی تو هستم. 🖐️")

# ----------------------------------------------------------------------

# هندلر برای ویدیوها
@bot.on_message(filters.video & filters.private)
async def process_video(client: Client, message: Message):
    # ۱. پیام در حال پردازش را ارسال کنید
    processing_msg = await message.reply_text("در حال دانلود ویدیو...")

    try:
        # ۲. ویدیوی ارسالی را دانلود کنید
        await message.download(file_name=INPUT_VIDEO_PATH)
        await processing_msg.edit_text("دانلود با موفقیت انجام شد. در حال اضافه کردن واترمارک...")

        # ۳. دستور FFmpeg برای اضافه کردن واترمارک
        # این دستور لوگو را در گوشه پایین سمت راست قرار می‌دهد
        ffmpeg_command = [
            "ffmpeg",
            "-i", INPUT_VIDEO_PATH,        # ورودی ویدیو
            "-i", WATERMARK_FILE,          # ورودی واترمارک (لوگو)
            "-filter_complex",
            # `overlay=main_w-overlay_w-10:main_h-overlay_h-10`
            # واترمارک را ۱۰ پیکسل از پایین و ۱۰ پیکسل از راست قرار می‌دهد.
            "[0:v][1:v]overlay=main_w-overlay_w-10:main_h-overlay_h-10[out]",
            "-map", "[out]",
            "-map", "0:a?", # کپی کردن استریم صوتی اگر وجود داشته باشد
            "-c:a", "copy",
            OUTPUT_VIDEO_PATH              # خروجی ویدیو
        ]

        # ۴. اجرای دستور FFmpeg
        # `subprocess.run` را به صورت غیرهمزمان اجرا می‌کنیم تا ربات مسدود نشود.
        process = await bot.loop.run_in_executor(
            None,
            lambda: subprocess.run(ffmpeg_command, capture_output=True, text=True)
        )

        if process.returncode != 0:
            await processing_msg.edit_text(
                f"❌ خطایی در اضافه کردن واترمارک رخ داد.\n\n**خطای FFmpeg:**\n`{process.stderr[:500]}`"
            )
            return

        await processing_msg.edit_text("واترمارک با موفقیت اضافه شد. در حال آپلود...")

        # ۵. ارسال ویدیوی خروجی
        await client.send_video(
            chat_id=message.chat.id,
            video=OUTPUT_VIDEO_PATH,
            caption="✅ اینم ویدیوی شما با واترمارک!"
        )

        await processing_msg.delete() # حذف پیام در حال پردازش

    except Exception as e:
        await processing_msg.edit_text(f"❌ یک خطای غیرمنتظره رخ داد: `{e}`")

    finally:
        # ۶. حذف فایل‌های موقت
        if os.path.exists(INPUT_VIDEO_PATH):
            os.remove(INPUT_VIDEO_PATH)
        if os.path.exists(OUTPUT_VIDEO_PATH):
            os.remove(OUTPUT_VIDEO_PATH)

# اجرای ربات
bot.run()
