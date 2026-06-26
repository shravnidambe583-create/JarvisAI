import requests
import json
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, OLLAMA_BASE_URL, OLLAMA_MODEL
from memory.db_manager import DatabaseManager

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class AIChat:
    """Manages conversational AI interfaces with OpenAI, Ollama, and offline Rule NLP."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self.openai_client = None
        
        if HAS_OPENAI and OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception as e:
                print(f"[AI] Failed to init OpenAI client: {e}")
                
        # Available personas
        self.persona = "default"
        self.personas = {
            "default": "You are JARVIS X, a highly advanced, loyal, and helpful desktop AI assistant inspired by Iron Man's JARVIS. You speak in a polite, professional, and slightly futuristic tone.",
            "stark": "You are JARVIS X. Speak in a witty, sarcastic, and conversational tone, like Tony Stark's assistant. Use phrases like 'Sir' or 'Boss' occasionally, but with a humorous, tech-savvy attitude.",
            "scientific": "You are JARVIS X, serving as a chief science officer assistant. Speak with high technical accuracy, using analytical terms, and break down complex concepts methodically.",
            "military": "You are JARVIS X operating in tactical combat protocol. Respond with brevity, strategic terms, and structured list items. Confirm actions with 'Affirmative Sir' or 'Protocol initiated'."
        }

    def set_persona(self, persona_name: str) -> bool:
        """Switch current personality mode."""
        p_name = persona_name.lower().strip()
        if p_name in self.personas:
            self.persona = p_name
            return True
        return False

    def is_ollama_available(self) -> bool:
        """Tests if local Ollama server is running and accessible."""
        try:
            resp = requests.get(OLLAMA_BASE_URL, timeout=1)
            return resp.status_code == 200
        except Exception:
            return False

    def chat(self, user_message: str) -> str:
        """Routes message to the best available AI engine (OpenAI -> Ollama -> Offline Fallback)."""
        # Save user message to database
        self.db.save_message("user", user_message)
        
        # Get last 6 messages of context memory
        history_rows = self.db.get_conversation_history(limit=6)
        
        # Build prompt messages
        system_instruction = self.personas.get(self.persona, self.personas["default"])
        
        response_text = ""
        
        # Method 1: OpenAI
        if self.openai_client:
            try:
                response_text = self._chat_openai(system_instruction, history_rows, user_message)
            except Exception as e:
                print(f"[AI] OpenAI failed: {e}. Falling back...")
                
        # Method 2: Ollama (Offline Local LLM)
        if not response_text and self.is_ollama_available():
            try:
                response_text = self._chat_ollama(system_instruction, history_rows, user_message)
            except Exception as e:
                print(f"[AI] Ollama failed: {e}. Falling back...")

        # Method 3: Offline Rule-Based NLP engine (Zero Internet / Zero LLM safety fallback)
        if not response_text:
            response_text = self._chat_offline_fallback(user_message)
            
        # Save assistant response
        self.db.save_message("assistant", response_text)
        return response_text

    def _chat_openai(self, system_instruction, history, user_message) -> str:
        """Helper to call OpenAI chat completion."""
        messages = [{"role": "system", "content": system_instruction}]
        
        # Append history
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["message"]})
            
        # Append current user prompt
        messages.append({"role": "user", "content": user_message})
        
        response = self.openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
        )
        return response.choices[0].message.content.strip()

    def _chat_ollama(self, system_instruction, history, user_message) -> str:
        """Helper to call Ollama local model."""
        prompt = f"System: {system_instruction}\n"
        for msg in history:
            prompt += f"{msg['role'].capitalize()}: {msg['message']}\n"
        prompt += f"User: {user_message}\nAssistant:"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        
        url = f"{OLLAMA_BASE_URL}/api/generate"
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()
        raise Exception(f"Ollama returned status code {response.status_code}")

    def _chat_offline_fallback(self, query: str) -> str:
        """A simple, smart offline rule-based NLP agent when no LLM is functional."""
        q = query.lower()
        
        # Match standard greetings / queries
        if any(greet in q for greet in ["hello", "hi", "hey jarvis", "wake up"]):
            if self.persona == "stark":
                return "At your service, Sir. What's on the agenda today?"
            return "Hello, Sir. I am online and ready to assist you. All systems are operating normally."
            
        elif "your name" in q:
            return "My designation is JARVIS X: Just A Rather Very Intelligent System (Version 2.0)."
            
        elif any(phrase in q for phrase in ["how are you", "system status", "diagnostics"]):
            total_tasks = len(self.db.get_tasks())
            return f"I am running at peak performance. Core CPU registers are normal. The database shows {total_tasks} active task entries in your workspace log."
            
        elif "thank you" in q or "thanks" in q:
            if self.persona == "stark":
                return "No problem. Just doing my job, boss."
            return "The pleasure is entirely mine, Sir."
            
        elif "help" in q:
            return "I can manage your desktop automations (open applications, set volume/brightness), manage a tasks checklist, secure your system via face recognition login, capture screenshots, and answer queries. Simply tell me a command."
            
        # Default smart response
        if self.persona == "stark":
            return "I'm currently disconnected from my main server link, Sir. I can't look that up, but the local hardware controls are still fully functional."
        return "I am currently running in offline standby mode without a server connection. I can execute local system controls, but conversational queries require an active connection or local Ollama engine."
