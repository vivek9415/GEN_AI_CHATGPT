from flask import Flask, request, render_template_string, session
import os
from dotenv import load_dotenv
import google.generativeai as genai
import markdown

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the SDK with your API key
genai.configure(api_key=GOOGLE_API_KEY)

# Create a Generative Model instance
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key for session management

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        user_input = request.form['question']
        session['chat_history'].append({"role": "user", "content": user_input})

        try:
            response = model.generate_content(user_input)
            ai_response = response.text if hasattr(response, 'text') else "No valid response text found."
            # Convert Markdown to HTML
            ai_response_html = markdown.markdown(ai_response)
        except Exception as e:
            ai_response_html = f"An error occurred: {str(e)}"
        
        session['chat_history'].append({"role": "ai", "content": ai_response_html})
    
    chat_history = session.get('chat_history', [])
    return render_template_string('''
        <!doctype html>
        <title>AI Chat</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
            .chat-container {
                max-width: 600px;
                margin: auto;
                height: 80vh;
                display: flex;
                flex-direction: column;
                border: 1px solid #ddd;
                border-radius: 8px;
                overflow: hidden;
            }
            .messages {
                flex: 1;
                padding: 10px;
                overflow-y: auto;
                border-bottom: 1px solid #ddd;
            }
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
                max-width: 80%;
                display: inline-block;
                clear: both;
            }
            .user {
                background-color: #e0f7fa;
                align-self: flex-end;
            }
            .ai {
                background-color: #f1f8e9;
                align-self: flex-start;
            }
            .message-content { white-space: pre-wrap; }
            .input-container {
                display: flex;
                border-top: 1px solid #ddd;
                background-color: #fff;
                padding: 10px;
                align-items: center;
            }
            input[type="text"] {
                flex: 1;
                padding: 10px;
                border-radius: 20px;
                border: 1px solid #ddd;
                margin-right: 10px;
                min-width: 400px;
            }
            input[type="submit"] {
                padding: 10px 20px;
                border: none;
                border-radius: 20px;
                background-color: #3498db;
                color: white;
                cursor: pointer;
            }
            input[type="submit"]:hover {
                background-color: #2980b9;
            }
            .spinner {
                border: 8px solid #f3f3f3;
                border-top: 8px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .hidden { display: none; }
        </style>
        <h1 style="text-align: center;">AI Chat</h1>
        <div class="chat-container">
            <div class="messages" id="chat-container">
                {% for message in chat_history %}
                    <div class="message {{ message.role }}">
                        <div class="message-content">{{ message.content | safe }}</div>
                    </div>
                {% endfor %}
            </div>
            <div id="spinner" class="spinner hidden"></div>
            <div class="input-container">
                <form id="chat-form" method="post" onsubmit="showSpinner()">
                    <input type="text" name="question" placeholder="Type your message..." required>
                    <input type="submit" value="Send">
                </form>
            </div>
        </div>
        <script>
            function showSpinner() {
                document.getElementById('spinner').classList.remove('hidden');
            }
            
            // Optionally, hide the spinner after form submission and response
            document.getElementById('chat-form').addEventListener('submit', function() {
                setTimeout(function() {
                    document.getElementById('spinner').classList.add('hidden');
                    document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
                }, 10000);  // Adjust the timeout duration as needed
            });
        </script>
        ''', chat_history=chat_history)

if __name__ == "__main__":
    app.run(debug=True)
