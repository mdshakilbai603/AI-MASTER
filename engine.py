import os
import subprocess
from flask import Flask, render_template, request, send_file
# ওপেন সোর্স লাইব্রেরি
from gtts import gTTS 
import whisper # pip install openai-whisper

app = Flask(__name__)

# ডিরেক্টরি সেটআপ
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Whisper মডেল লোড করা (এটি একবারই ডাউনলোড হবে)
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/render', methods=['POST'])
def render_engine():
    video = request.files['video']
    task = request.form.get('task')
    
    input_p = os.path.join(UPLOAD_FOLDER, video.filename)
    output_p = os.path.join(OUTPUT_FOLDER, "AI_FREE_" + video.filename)
    video.save(input_p)

    # --- ফ্রি ডাবিং লজিক ---
    if task == "dubbing":
        # ১. অডিও এক্সট্রাক্ট
        subprocess.run(f"ffmpeg -i {input_p} -vn -acodec mp3 temp.mp3 -y", shell=True)
        
        # ২. ফ্রি স্পিচ টু টেক্সট (Whisper)
        result = model.transcribe("temp.mp3")
        original_text = result['text']
        
        # ৩. ফ্রি ট্রান্সলেশন এবং ভয়েস (gTTS)
        tts = gTTS(text=original_text, lang='bn') # সরাসরি বাংলায় ডাবিং
        tts.save("dubbed_audio.mp3")

        # ৪. অডিও ভিডিও মার্জ
        subprocess.run(f"ffmpeg -i {input_p} -i dubbed_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest {output_p} -y", shell=True)

    # --- ফ্রি এডিটিং ফিচারস ---
    elif task == "slowmo":
        subprocess.run(f"ffmpeg -i {input_p} -vf 'minterpolate=fps=60,setpts=2*PTS' {output_p} -y", shell=True)

    return send_file(output_p, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
