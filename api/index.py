import sys
import os
from flask import Flask, jsonify, request, Response
import tempfile
import edge_tts
import asyncio

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_chat import AIChat
from memory.db_manager import DatabaseManager

app = Flask(__name__)

# Initialize database and AI chat layers
db = DatabaseManager()
ai = AIChat(db)

@app.route('/api/tts', methods=['GET'])
def text_to_speech_api():
    """Synthesizes text into high-fidelity speech bytes using edge-tts."""
    text = request.args.get("text", "")
    voice = request.args.get("voice", "en-US-EmmaMultilingualNeural")
    
    if not text:
        return jsonify({"error": "No 'text' parameter provided"}), 400
        
    try:
        # Create unique temp file path
        temp_dir = tempfile.gettempdir()
        temp_filename = f"tts_{os.urandom(8).hex()}.mp3"
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        # Async run edge-tts to save file
        async def run_tts():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(temp_filepath)
            
        asyncio.run(run_tts())
        
        # Read the file bytes into memory and clean up file immediately
        if os.path.exists(temp_filepath):
            with open(temp_filepath, "rb") as f:
                audio_data = f.read()
            try:
                os.remove(temp_filepath)
            except Exception:
                pass
            return Response(audio_data, mimetype="audio/mpeg")
        else:
            return jsonify({"error": "Failed to synthesize speech file"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "JARVIS X AI Mainframe API",
        "version": "2.1.0",
        "description": "Exposes the conversational brain and task tracking systems of your JARVIS X assistant serverless on Vercel."
    })

@app.route('/api/chat', methods=['GET', 'POST'])
def chat():
    """Allows sending chat queries to the JARVIS X AI Brain."""
    if request.method == 'POST':
        # Retrieve JSON body
        data = request.get_json() or {}
        message = data.get("message", "")
    else:
        # Retrieve query parameter
        message = request.args.get("message", "")
        
    if not message:
        return jsonify({"error": "No 'message' parameter provided in request."}), 400
        
    # Execute conversation query
    reply = ai.chat(message)
    
    return jsonify({
        "query": message,
        "reply": reply,
        "persona": ai.persona
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Fetches the active mission and task checklist."""
    tasks = db.get_tasks()
    return jsonify({
        "count": len(tasks),
        "tasks": tasks
    })

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
