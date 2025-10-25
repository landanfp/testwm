# استفاده از یک ایمیج پایه رسمی پایتون برای محیط‌های سبک
FROM python:3.11-slim-buster

# نصب FFmpeg
# RUN apt-get update: لیست پکیج‌ها را به‌روز می‌کند
# RUN apt-get install -y ffmpeg: FFmpeg را نصب می‌کند
# RUN rm -rf /var/lib/apt/lists/*: فایل‌های کش را برای کاهش حجم ایمیج حذف می‌کند
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# تنظیم دایرکتوری کاری درون کانتینر
WORKDIR /app

# کپی کردن فایل‌های مورد نیاز
# requirements.txt را کپی کرده و وابستگی‌ها را نصب می‌کند
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن فایل‌های ربات و واترمارک
# bot.py: فرض می‌کنیم کد پایتون شما در فایلی به نام bot.py ذخیره شده است
# logo.png: فایل واترمارک
COPY bot.py .
COPY logo.png .

# دستور اجرای ربات هنگام شروع کانتینر
# مطمئن شوید که نام فایل پایتون شما با bot.py مطابقت داشته باشد
CMD ["python", "bot.py"]
