from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Configure ton API Key OpenAI
openai.api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_url = request.json.get('audio_url')
    
    # Appelle l'API d'OpenAI pour transcrire l'audio
    response = openai.Audio.transcribe(
        model="whisper-1",
        file_url=audio_url
    )
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
