import os
import subprocess
from flask import Flask, render_template, request, send_file
from gtts import gTTS

app = Flask(__name__)

# ফাইল সেভ করার ডিরেক্টরি
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'processed'
for f in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(f, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/edit', methods=['POST'])
def edit_video():
    if 'video' not in request.files:
        return "ভিডিও পাওয়া যায়নি", 400
    
    video = request.files['video']
    task = request.form.get('task', 'cinematic')
    
    in_path = os.path.join(UPLOAD_FOLDER, video.filename)
    out_path = os.path.join(OUTPUT_FOLDER, "EDITED_" + video.filename)
    video.save(in_path)

    try:
        if task == 'cinematic':
            # হাই-কোয়ালিটি কালার গ্রেডিং
            cmd = f"ffmpeg -i '{in_path}' -vf \"eq=brightness=0.03:contrast=1.3:saturation=1.5,unsharp=5:5:1.0:5:5:0.0\" -c:a copy '{out_path}' -y"
        
        elif task == 'slowmo':
            # স্মুথ স্লো মোশন
            cmd = f"ffmpeg -i '{in_path}' -vf \"setpts=2.5*PTS\" -af \"atempo=0.5\" '{out_path}' -y"
            
        elif task == 'dubbing':
            # ডাবিং ফিচারের জন্য হালকা কোড
            tts = gTTS(text="ভিডিও ডাবিং সফল হয়েছে।", lang='bn')
            tts.save("voice.mp3")
            cmd = f"ffmpeg -i '{in_path}' -i voice.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest '{out_path}' -y"
            
        else:
            cmd = f"ffmpeg -i '{in_path}' -c copy '{out_path}' -y"

        # কমান্ড রান করা
        subprocess.run(cmd, shell=True, check=True)
        return send_file(out_path, mimetype='video/mp4')

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Render-এর ৫০২ এরর সমাধান করার জন্য পোর্ট সেটআপ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
