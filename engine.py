import os
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from openai import OpenAI
import requests

app = Flask(__name__)

# আপনার দেওয়া API Keys সরাসরি কোডে যুক্ত করা হলো
Gemini_API_KEY = "AIzaSyD5jIL3FPgjAyOKKVTJCTZdhhHpeGztPuY"
HF_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

# ডিরেক্টরি সেটআপ
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/render', methods=['POST'])
def render_engine():
    video = request.files['video']
    task = request.form.get('task')
    target_lang = request.form.get('target_lang', 'bn') # ডিফল্ট বাংলা
    
    input_path = os.path.join(UPLOAD_FOLDER, video.filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"AI_MASTER_{video.filename}")
    video.save(input_path)

    # --- ১. গ্লোবাল ডাবিং ফিচার (OpenAI + FFmpeg) ---
    if task == "dubbing":
        # অডিও বের করা
        subprocess.run(f"ffmpeg -i {input_path} -vn -acodec mp3 temp_audio.mp3 -y", shell=True)
        
        # Whisper দিয়ে ভয়েস থেকে টেক্সট (OpenAI)
        audio_file = open("temp_audio.mp3", "rb")
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        
        # যেকোনো ভাষা থেকে বাংলায় ডাবিং (GPT-4)
        translation = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Translate this text to {target_lang} for voice dubbing: {transcript.text}"}]
        )
        translated_text = translation.choices[0].message.content

        # টেক্সট থেকে এআই ভয়েস (TTS)
        response = client.audio.speech.create(model="tts-1", voice="onyx", input=translated_text)
        response.stream_to_file("translated_audio.mp3")

        # ভিডিওর সাথে নতুন ভয়েস জোড়া লাগানো
        subprocess.run(f"ffmpeg -i {input_path} -i translated_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest {output_path} -y", shell=True)

    # --- ২. Hugging Face AI ফিচার (Object Recognition/Enhance) ---
    elif task == "ai_enhance":
        API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        # এখানে Hugging Face মডেলের কাজ চলবে...
        subprocess.run(f"ffmpeg -i {input_path} -vf unsharp=5:5:1.0:5:5:0.0 {output_path} -y", shell=True)

    # --- ৩. ১০০টি ফিচারের তালিকা অনুযায়ী প্রসেসিং ---
    elif task == "slowmo":
        subprocess.run(f"ffmpeg -i {input_path} -filter:v 'setpts=2.0*PTS' {output_path} -y", shell=True)
    
    elif task == "4k_upscale":
        subprocess.run(f"ffmpeg -i {input_path} -vf scale=3840:2160:flags=lanczos {output_path} -y", shell=True)

    return send_file(output_path, mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
