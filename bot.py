from pyrogram import Client, filters
from watermark import add_animated_watermark
import os

API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '8189638115:AAEYMDvummCXAPgdpavZbYHa3YuXpOzkRBY'

app = Client("watermark-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "👋 سلام! ویدیوت رو بفرست تا واترمارک متحرک روی اون اضافه کنم 🎬"
    )

@app.on_message(filters.video)
async def handle_video(_, message):
    video = await message.download()
    await message.reply_text("⏳ در حال پردازش واترمارک متحرک روی ویدیو...")

    output = f"out_{message.video.file_unique_id}.mp4"
    add_animated_watermark(video, "logo.png", output)

    await message.reply_video(video=output, caption="✅ واترمارک اضافه شد!")
    os.remove(video)
    os.remove(output)

app.run()
