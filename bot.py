import os
import asyncio
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '5355055672:AAEE8OIOqLYxbnwesF3ki2sOsXr03Q90JiI'
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه

app = Client("watermark_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

LOGO_PATH = "logo.gif"  # فایل واترمارک موشن
OUTPUT_DIR = "downloads"

os.makedirs(OUTPUT_DIR, exist_ok=True)

async def add_watermark(input_path, output_path):
    """افزودن واترمارک GIF به ویدیو"""
    try:
        input_video = ffmpeg.input(input_path)
        overlay = ffmpeg.input(LOGO_PATH)

        (
            ffmpeg
            .output(
                input_video,
                overlay,
                output_path,
                vf="movie=logo.gif[wm];[in][wm]overlay=W-w-20:H-h-20:shortest=1[out]",
                vcodec="libx264",
                acodec="aac",
                strict="experimental"
            )
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        return True
    except Exception as e:
        print("FFmpeg Error:", e)
        return False


@app.on_message(filters.video)
async def watermark_handler(client, message: Message):
    status = await message.reply_text("📥 در حال دریافت ویدیو...")

    video = await message.download(file_name=os.path.join(OUTPUT_DIR, "input.mp4"))
    await status.edit("🎞 در حال افزودن واترمارک متحرک...")

    output_path = os.path.join(OUTPUT_DIR, "output.mp4")
    success = await add_watermark(video, output_path)

    if not success:
        await status.edit("❌ خطا در افزودن واترمارک!")
        return

    await status.edit("📤 در حال آپلود ویدیو...")
    await message.reply_video(video=output_path, caption="✅ واترمارک اضافه شد!")
    await status.delete()

    # حذف فایل‌ها بعد از ارسال
    try:
        os.remove(video)
        os.remove(output_path)
    except:
        pass


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "👋 سلام! ویدیوت رو بفرست تا واترمارک متحرک بهش اضافه کنم 🎬"
    )


print("✅ Bot is running...")
app.run()
