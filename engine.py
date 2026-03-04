import os
import subprocess
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_engine():
    video = request.files['video']
    feature_type = request.form.get('feature') # এখানে আপনার ১০০টি ফিচারের আইডি আসবে
    
    input_p = "uploads/" + video.filename
    output_p = "processed/ai_pro_" + video.filename
    video.save(input_p)

    # ১০০টি ফিচারের লজিক ডাইনামিকালি এখানে কাজ করবে
    commands = {
        "bg_remove": f"ffmpeg -i {input_p} -vf 'colorkey=0x00FF00:0.1:0.2' {output_p}", # AI BG
        "slow_mo": f"ffmpeg -i {input_p} -filter:v 'setpts=2.0*PTS' {output_p}",        # Slow Motion
        "cinematic": f"ffmpeg -i {input_p} -vf 'curves=vintage,hue=s=1.2' {output_p}", # Cinema Mode
        "stabilize": f"ffmpeg -i {input_p} -vf 'vidstabdetect,vidstabtransform' {output_p}", # Video Stabilizer
        "sharpen": f"ffmpeg -i {input_p} -vf 'unsharp=5:5:1.0:5:5:0.0' {output_p}"     # 4K Sharpening
    }

    selected_cmd = commands.get(feature_type, f"ffmpeg -i {input_p} {output_p}")
    subprocess.run(selected_cmd, shell=True)
    
    return send_file(output_p, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(port=10000)
