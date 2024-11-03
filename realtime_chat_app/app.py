# app.py
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json
import os


app = Flask(__name__)
CORS(app)

# Configure OpenAI API key
OPENAI_API_KEY = 'OPENAI_API_KEY'
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')


# File path for conversation history storage
HISTORY_FILE = 'conversation_history.json'

def load_history():
    """Load conversation history from a JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return [{'role': 'system', 'content': 'You are a helpful assistant.'}]

def save_history(history):
    """Save conversation history to a JSON file."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    # Load existing conversation history
    history = load_history()

    # Append the new user message to history
    history.append({'role': 'user', 'content': user_message})

    try:
        # Call the OpenAI API with the entire conversation history
        response = client.chat.completions.create(
            model='gpt-4',
            messages=history
        )

        # Get AI response and add it to the conversation history
        ai_response = response.choices[0].message.content
        history.append({'role': 'assistant', 'content': ai_response})

        # Save updated history back to the JSON file
        save_history(history)

        return jsonify({'response': ai_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to clear JSON history file if needed
@app.route('/clear', methods=['POST'])
def clear_history():
    save_history([{'role': 'system', 'content': 'You are a helpful assistant.'}])
    return jsonify({'status': 'History cleared'}), 200



if __name__ == '__main__':
    app.run(debug=False)