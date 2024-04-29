from flask import Flask, request, jsonify
import os
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    video_file = request.files['video']
    client = speech_v1.SpeechClient()
    audio = {"uri": video_file.filename}
    config = {
        "enable_word_time_offsets": True,
        "language_code": "en-US",
        "sample_rate_hertz": 16000,
    }
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=90)

    results = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            results.append({
                "word": word,
                "start_time": start_time.seconds + start_time.nanos * 1e-9,
                "end_time": end_time.seconds + end_time.nanos * 1e-9,
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
