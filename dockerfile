FROM python:3.11-slim-bullseye
WORKDIR /app
COPY requirements.txt ./
RUN apt update && apt install git -y
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python3", "/app/bot.py" ]