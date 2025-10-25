# استفاده از ایمیج پایه جدیدتر Debian 12 (Bookworm)
FROM python:3.11-slim-bookworm

# نصب FFmpeg
# Bookworm به صورت پیش‌فرض شامل FFmpeg است
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری درون کانتینر
WORKDIR /app

# کپی کردن فایل‌های مورد نیاز
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن فایل‌های ربات و واترمارک
COPY bot.py .
COPY logo.png .

# دستور اجرای ربات
CMD ["python", "bot.py"]
