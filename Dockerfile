# استفاده از ایمیج پایه جدیدتر Debian 12 (Bookworm)
FROM python:3.11-slim-bookworm

# ۱. فعال کردن مخازن contrib و non-free
# این کار به apt اجازه می‌دهد پکیج‌هایی مانند libx264 را پیدا کند.
RUN echo "deb http://deb.debian.org/debian bookworm main contrib non-free" > /etc/apt/sources.list.d/bookworm.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list.d/bookworm.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list.d/bookworm.list

# ۲. نصب FFmpeg و انکودر libx264
# apt-get update باید دوباره اجرا شود تا مخازن جدید بارگذاری شوند.
RUN apt-get update && \
    apt-get install -y ffmpeg libx264 && \
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
