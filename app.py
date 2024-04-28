from flask import Flask, request, jsonify
import os
import whisper

app = Flask(__name__)
model = whisper.load_model("base")  # Load the Whisper model

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return "No audio file provided", 400

    audio_file = request.files['audio']
    audio_file.save("temp_audio.webm")  # Save the uploaded file locally

    result = model.transcribe("temp_audio.webm")  # Transcribe the audio
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Default to 5000 if PORT not set
