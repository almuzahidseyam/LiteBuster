from flask import Flask, render_template_string, send_file, session, jsonify, request
import random
import string
from gtts import gTTS
import io

app = Flask(__name__)
app.secret_key = 'litebuster_super_secret_demo_key'

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LiteBuster CAPTCHA Demo</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #0f172a; margin: 0; color: white;}
        .captcha-box { background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3); text-align: center; width: 350px; border: 1px solid #334155;}
        .title { font-size: 22px; font-weight: bold; color: #f8fafc; margin-bottom: 20px; }
        canvas { width: 100%; height: 80px; background: #0f172a; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155;}
        audio { width: 100%; margin-bottom: 20px; outline: none; border-radius: 8px;}
        input { padding: 12px; width: calc(100% - 24px); border: 2px solid #334155; border-radius: 6px; font-size: 16px; margin-bottom: 20px; text-align: center; text-transform: uppercase; letter-spacing: 2px; background: #0f172a; color: white;}
        input:focus { border-color: #38bdf8; outline: none; }
        .verify-btn { padding: 12px; width: 100%; background: #38bdf8; color: #0f172a; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.2s; }
        .verify-btn:hover { background: #0284c7; color: white; }
        #result { margin-top: 15px; font-weight: bold; height: 24px; font-size: 14px;}
    </style>
</head>
<body>
    <div class="captcha-box">
        <div class="title">Secure Audio Verification</div>
        <canvas id="visualizer"></canvas>
        <audio controls src="/audio" id="captcha-audio" crossorigin="anonymous"></audio>
        <input type="text" id="captcha-input" placeholder="Enter Audio Code" maxlength="5">
        <button class="verify-btn" onclick="verify()">Verify Human</button>
        <p id="result"></p>
    </div>
    
    <script>
        // Live Audio Waveform Visualizer
        const audio = document.getElementById('captcha-audio');
        const canvas = document.getElementById('visualizer');
        const ctx = canvas.getContext('2d');
        let audioCtx;
        let analyser;
        let source;

        audio.onplay = () => {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                source = audioCtx.createMediaElementSource(audio);
                source.connect(analyser);
                analyser.connect(audioCtx.destination);
                analyser.fftSize = 256;
            }
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            
            function draw() {
                if (!audio.paused) requestAnimationFrame(draw);
                analyser.getByteTimeDomainData(dataArray);
                ctx.fillStyle = '#0f172a';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#38bdf8';
                ctx.beginPath();
                const sliceWidth = canvas.width * 1.0 / bufferLength;
                let x = 0;
                for (let i = 0; i < bufferLength; i++) {
                    const v = dataArray[i] / 128.0;
                    const y = v * canvas.height / 2;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                    x += sliceWidth;
                }
                ctx.lineTo(canvas.width, canvas.height / 2);
                ctx.stroke();
            }
            draw();
        };

        async function verify() {
            const answer = document.getElementById('captcha-input').value;
            const res = await fetch('/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({answer: answer})
            });
            const data = await res.json();
            const resultEl = document.getElementById('result');
            if (data.success) {
                resultEl.innerText = "✅ Verification Successful!";
                resultEl.style.color = "#34d399";
                setTimeout(() => location.reload(), 2000);
            } else {
                resultEl.innerText = "❌ Incorrect. Try again.";
                resultEl.style.color = "#f87171";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    challenge = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session['challenge'] = challenge
    return render_template_string(HTML)

@app.route('/audio')
def audio():
    challenge = session.get('challenge', 'ERROR')
    spoken_text = ' '.join(list(challenge))
    tts = gTTS(text=spoken_text, lang='en', slow=True)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return send_file(fp, mimetype='audio/mpeg', as_attachment=False, download_name='challenge.mp3')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    user_answer = data.get('answer', '').strip().upper()
    correct_answer = session.get('challenge', '')
    if user_answer and user_answer == correct_answer:
        return jsonify({'success': True})
    return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
