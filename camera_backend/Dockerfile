FROM python:3.11-bookworm

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

COPY camera_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY camera_backend .

ENV host=0.0.0.0
ENV port=8001
ENV image_save_path=/data/captures
ENV video_save_path=/data/videos

VOLUME ["/data"]
EXPOSE 8001

CMD ["python", "main.py"]
