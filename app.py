from flask import Flask, request, jsonify
import os
from google.cloud import speech

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    video_file = request.files['video']
    client = speech.SpeechClient()

    audio_content = video_file.read()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        enable_word_time_offsets=True,
        language_code="en-US",
        sample_rate_hertz=16000,
    )
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)

    results = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            results.append({
                "word": word,
                "start_time": start_time,
                "end_time": end_time,
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
