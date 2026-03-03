# হাই-পারফরম্যান্স এআই বেস ইমেজ
FROM python:3.10-slim-buster

# সিস্টেম লাইব্রেরি (FFmpeg, OpenCV, Google Cloud SDK)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# HuggingFace এবং এআই মডেল লাইব্রেরি অটো-ইনস্টল
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r requirements.txt

# গিটহাব থেকে সরাসরি সোর্স কোড এবং মডেল সিঙ্কিং
COPY . .

# এআই ইঞ্জিন স্টার্ট
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "engine:app", "--timeout", "0"]
