FROM nvidia/cuda:12.0-base-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3-pip ffmpeg git libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# AI মডেল ডাউনলোড (HuggingFace থেকে)
RUN python3 -c "import torch; print('CUDA Available:', torch.cuda.is_available())"

COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "engine:app", "--timeout", "0"]
