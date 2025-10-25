from pyrogram import Client, filters
import os
import subprocess
import time

# تنظیمات ربات
API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '5355055672:AAEE8OIOqLYxbnwesF3ki2sOsXr03Q90JiI'
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه

LOGO_PATH = "logo.png"      # لوگوی motion
DOWNLOAD_PATH = "downloads"

# ساخت پوشه دانلود اگر نبود
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

bot = Client("motion_logo_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# پیام شروع
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 سلام! ویدیو بفرست تا لوگوی motion بهش اضافه کنم.")

# دریافت ویدیو
@bot.on_message(filters.video)
async def add_motion_logo(client, message):
    msg = await message.reply_text("⏳ در حال دانلود ویدیو...")

    # دانلود ویدیو
    video_path = await message.download(file_name=f"{DOWNLOAD_PATH}/{message.video.file_name}")

    await msg.edit_text("🎬 در حال افزودن واترمارک متحرک...")

    output_path = f"{DOWNLOAD_PATH}/out_{int(time.time())}.mp4"

    # دستور FFmpeg برای افزودن لوگو با افکت ورودی و خروجی (مثل GIF ارسالی تو)
    ffmpeg_cmd = f"""
    ffmpeg -y -i "{video_path}" -loop 1 -i "{LOGO_PATH}" -filter_complex "
    [1:v]format=rgba,
     fade=t=in:st=0:d=1.2:alpha=1,
     fade=t=out:st=3.8:d=1.2:alpha=1,
     scale=iw*0.25:ih*0.25,
     translate=x=(W-w)/2:y=(H-h)/2,
     setpts=PTS-STARTPTS[logo];
    [0:v][logo]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,5)'[v]
    " -map "[v]" -map 0:a? -c:a copy -c:v libx264 -crf 18 -preset medium "{output_path}"
    """

    subprocess.run(ffmpeg_cmd, shell=True)

    await msg.edit_text("📤 در حال آپلود ویدیو...")

    # ارسال خروجی به کاربر
    await client.send_video(
        chat_id=message.chat.id,
        video=output_path,
        caption="✅ ویدیو با لوگوی motion آماده شد!"
    )

    # حذف فایل‌های موقت
    try:
        os.remove(video_path)
        os.remove(output_path)
    except:
        pass

    await msg.delete()

print("🤖 Bot started...")
bot.run()
