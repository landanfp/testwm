import os
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# --- تنظیمات ربات ---
API_ID = '3335796'
API_HASH = '138b992a0e672e8346d8439c3f42ea78'
BOT_TOKEN = '5355055672:AAEE8OIOqLYxbnwesF3ki2sOsXr03Q90JiI'
#LOG_CHANNEL = -1001792962793  # مقدار دلخواه
# ساخت کلاینت
bot = Client("simple_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- تنظیمات FFmpeg و لوگو ---
# مسیر فایل لوگوی شما (باید در کنار اسکریپت باشد)
LOGO_PATH = "logo.png"

# تنظیمات افکت لوگو
LOGO_DURATION = 4.0    # مدت‌زمان هر نمایش لوگو (به ثانیه)
FADE_IN_TIME = 1.2     # مدت‌زمان افکت ورودی
FADE_OUT_TIME = 1.2    # مدت‌زمان افکت خروجی

# --- توابع کمکی ---

def process_video(video_path: str, logo_path: str, output_path: str, duration: float) -> tuple[bool, str]:
    """
    اجرای دستور FFmpeg برای ترکیب لوگوی متحرک با ویدیو
    خروجی: (وضعیت موفقیت‌آمیز، پیام خطا/موفقیت)
    """
    
    # دستور FFmpeg
    # این دستور لوگو را متحرک کرده (scale + fade) و به طور مداوم تکرار می‌کند.
    # [1:v] جریان لوگو
    # scale: انیمیشن بزرگ شدن لوگو در طول زمان LOGO_DURATION (4 ثانیه) با استفاده از تابع mod
    # fade: اعمال fade in/out بر اساس LOGO_DURATION
    # [0:v][logo_animated]overlay: ترکیب با ویدیو اصلی در موقعیت 10:10 (گوشه بالا چپ)
    
    cmd = f"""
ffmpeg -y -i "{video_path}" -i "{logo_path}" -filter_complex "
# 1. متحرک‌سازی لوگو
[1:v]
 format=yuva444p,
 # افکت Scale و بزرگ شدن لوگو در طول 4 ثانیه و تکرار آن با mod(t, 4)
 scale=w='iw*(0.6+0.4*mod(t,{LOGO_DURATION})/{FADE_IN_TIME})':h='ih*(0.6+0.4*mod(t,{LOGO_DURATION})/{FADE_IN_TIME})',
 # افکت Fade In و Fade Out (برای لوگو، نه کل ویدیو)
 fade=t=in:st=0:d={FADE_IN_TIME}:alpha=1,
 fade=t=out:st=({duration}-{FADE_OUT_TIME}):d={FADE_OUT_TIME}:alpha=1
[logo_animated];

# 2. ترکیب لوگو با ویدیو (overlay)
[0:v][logo_animated]overlay=10:10:shortest=1[v]
" -map "[v]" -map 0:a? -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "{output_path}"
"""
    
    try:
        # اجرای subprocess با check=True برای تولید CalledProcessError در صورت شکست FFmpeg
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True # برای decode کردن خروجی
        )
        return True, result.stderr

    except subprocess.CalledProcessError as e:
        # اگر FFmpeg با خطا خارج شود، پیام خطا را برمی‌گرداند
        error_message = f"FFmpeg Error (Exit Code {e.returncode}):\n\n{e.stderr}"
        print(error_message) # نمایش در کنسول سرور
        return False, error_message
        
    except FileNotFoundError:
        # اگر دستور ffmpeg پیدا نشود
        return False, "خطا: FFmpeg نصب نشده یا در PATH سیستم نیست."


# --- هندلر پیام ---

@bot.on_message(filters.video & filters.private)
async def video_handler(client: Client, message: Message):
    """
    دریافت ویدیو، افزودن لوگوی متحرک و ارسال مجدد
    """
    # 0. بررسی وجود لوگو
    if not os.path.exists(LOGO_PATH):
        await message.reply_text(f"خطا: فایل لوگو `{LOGO_PATH}` پیدا نشد. لطفاً مطمئن شوید فایل لوگو کنار اسکریپت قرار دارد.")
        return

    # 1. دانلود فایل ویدیو
    status_msg = await message.reply_text("📥 در حال دانلود ویدیو...")
    try:
        input_path = await message.download()
    except Exception as e:
        await status_msg.edit(f"❌ خطا در دانلود: {e}")
        return

    # 2. تعریف مسیر خروجی و مدت زمان
    video_duration = message.video.duration
    output_path = input_path + "_with_logo.mp4"
    
    # 3. پردازش ویدیو با FFmpeg
    await status_msg.edit("✨ در حال افزودن لوگوی متحرک (FFmpeg)...")
    
    # فراخوانی تابع عیب‌یابی شده
    success, error_msg = process_video(input_path, LOGO_PATH, output_path, video_duration)
    
    if success:
        # 4. آپلود و ارسال ویدیو
        await status_msg.edit("📤 در حال آپلود ویدیو...")
        try:
            await client.send_video(
                chat_id=message.chat.id,
                video=output_path,
                caption="✅ ویدیوی شما با لوگوی متحرک آماده شد!"
            )
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit(f"❌ خطا در آپلود: {e}")
            
    else:
        # 5. در صورت خطا، پیام خطا را به کاربر نشان می‌دهیم.
        # پیام خطا را در یک بلاک کد برای خوانایی بهتر قرار می‌دهیم.
        await status_msg.edit(f"❌ پردازش ویدیو با خطا مواجه شد:\n\nجزئیات خطا:\n```bash\n{error_msg[:1000]}\n```")

    # 6. پاکسازی فایل‌های موقت
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)


@bot.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "سلام 👋\nویدیو خود را ارسال کنید تا لوگوی متحرک بر روی آن قرار داده شود."
    )

# اجرا
if __name__ == "__main__":
    print("🤖 ربات Pyrogram در حال اجرا است...")
    bot.run()
