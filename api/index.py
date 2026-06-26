import sys
import os
from flask import Flask, jsonify, request

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_chat import AIChat
from memory.db_manager import DatabaseManager

app = Flask(__name__)

# Initialize database and AI chat layers
db = DatabaseManager()
ai = AIChat(db)

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
