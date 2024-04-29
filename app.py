from google.cloud import speech
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    if 'video' not in request.files:
        return "No file uploaded.", 400

    video_file = request.files['video']
    audio_content = video_file.read()

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        enable_word_time_offsets=True,
        language_code="en-US",
        sample_rate_hertz=16000,
        audio_channel_count=2,
        enable_automatic_punctuation=True
    )

    response = client.recognize(config=config, audio=audio)
    results = []

    for result in response.results:
        for alternative in result.alternatives:
            results.append({
                "transcript": alternative.transcript,
                "confidence": alternative.confidence
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
