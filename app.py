from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Configure ton API Key OpenAI à partir des variables d'environnement
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_url = request.json.get('audio_url')
    
    # Vérifie que l'URL audio est fournie
    if not audio_url:
        return jsonify({"error": "audio_url is required"}), 400

    try:
        # Appelle l'API d'OpenAI pour transcrire l'audio
        response = openai.Audio.transcribe(
            model="whisper-1",
            file_url=audio_url
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
