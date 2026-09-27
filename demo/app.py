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
        body { font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f3f4f6; margin: 0; }
        .captcha-box { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); text-align: center; width: 320px; }
        .title { font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 20px; }
        audio { width: 100%; margin-bottom: 20px; outline: none; }
        input { padding: 12px; width: calc(100% - 24px); border: 2px solid #e5e7eb; border-radius: 6px; font-size: 16px; margin-bottom: 20px; text-align: center; text-transform: uppercase; letter-spacing: 2px; }
        input:focus { border-color: #6366f1; outline: none; }
        button { padding: 12px; width: 100%; background: #6366f1; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; transition: background 0.2s; }
        button:hover { background: #4f46e5; }
        #result { margin-top: 15px; font-weight: bold; height: 24px; }
    </style>
</head>
<body>
    <div class="captcha-box">
        <div class="title">Audio Verification</div>
        <audio controls src="/audio" id="captcha-audio" autoplay></audio>
        <input type="text" id="captcha-input" placeholder="Enter Audio Code" maxlength="5">
        <button onclick="verify()">Verify</button>
        <p id="result"></p>
    </div>
    <script>
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
                resultEl.style.color = "#10b981";
                setTimeout(() => location.reload(), 2000);
            } else {
                resultEl.innerText = "❌ Incorrect. Try again.";
                resultEl.style.color = "#ef4444";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    # Generate random 5 char string (uppercase letters and digits)
    challenge = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    session['challenge'] = challenge
    return render_template_string(HTML)

@app.route('/audio')
def audio():
    challenge = session.get('challenge', 'ERROR')
    # Add spaces between characters so TTS spells it out clearly letter-by-letter
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
    print("Starting LiteBuster Demo CAPTCHA Server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
