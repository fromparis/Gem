from flask import Flask, request, jsonify, render_template
import openai
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure l'API Key OpenAI en utilisant les secrets
openai.api_key = os.getenv('OPENAI_API_KEY')

# Répertoire de téléchargement
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Appelle l'API d'OpenAI pour transcrire l'audio
        audio_file = open(file_path, "rb")
        response = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
