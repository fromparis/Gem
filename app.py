from flask import Flask, request, jsonify
import os
from groq import Groq

app = Flask(__name__)

# Initialize Groq client using the environment variable
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    # Extract user message from the POST request
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    # Create a chat completion using the Groq API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="mixtral-8x7b-32768",
    )

    # Return the model's response as JSON
    return jsonify({'response': chat_completion.choices[0].message.content})

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)
