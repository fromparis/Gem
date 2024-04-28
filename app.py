from flask import Flask, request, jsonify
import whisper

app = Flask(__name__)
model = whisper.load_model("base")  # Load a Whisper model; choose the model size that suits your needs

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return "No audio file provided", 400

    audio_file = request.files['audio']
    audio_file.save("temp_audio.webm")  # Save the uploaded audio file

    # Process the audio file with Whisper
    result = model.transcribe("temp_audio.webm")
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
