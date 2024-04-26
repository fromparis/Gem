from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="mixtral-8x7b-32768",
    )

    return jsonify({'response': chat_completion.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)
