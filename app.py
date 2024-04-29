import os
import json
from flask import Flask

app = Flask(__name__)

@app.route('/')
def check_env():
    # Attempt to fetch the environment variable
    json_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

    # Check if the environment variable is set
    if json_credentials is None:
        return "Environment variable not set."
    else:
        try:
            # Try to parse the JSON to see if it's correctly formatted
            credentials_dict = json.loads(json_credentials.replace('\\n', '\n'))
            return f"Credentials are set correctly: {credentials_dict['project_id']}"
        except Exception as e:
            return f"Error parsing credentials: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
