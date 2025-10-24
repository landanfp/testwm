FROM python:3.11-slim

# نصب ffmpeg و ابزارها
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "bot.py"]
