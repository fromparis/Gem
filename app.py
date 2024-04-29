from flask import Flask, request, jsonify
from google.cloud import speech
from moviepy.editor import VideoFileClip
from io import BytesIO
import os

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    # Check if the file part is present in the request
    if 'video' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    # Retrieve the file from the post request
    file = request.files['video']

    # Check if the filename is empty (no file)
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Use MoviePy to extract audio from video
        video_clip = VideoFileClip(file)
        audio_clip = video_clip.audio
        audio_bytes = BytesIO()
        audio_clip.write_audiofile(audio_bytes, codec='pcm_s16le', nbytes=2, fps=16000)
        audio_bytes = audio_bytes.getvalue()
    except Exception as e:
        return jsonify({"error": "Error processing video file", "details": str(e)}), 500

    # Initialize Google Cloud Speech client
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        enable_word_time_offsets=True,
        language_code="en-US",
        sample_rate_hertz=16000,
        audio_channel_count=2,
        enable_automatic_punctuation=True
    )

    # Perform synchronous speech recognition
    response = client.recognize(config=config, audio=audio)
    results = []

    # Parse results
    for result in response.results:
        alternatives = result.alternatives
        best_alternative = alternatives[0]  # Most likely result
        results.append({
            "transcript": best_alternative.transcript,
            "confidence": best_alternative.confidence
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
