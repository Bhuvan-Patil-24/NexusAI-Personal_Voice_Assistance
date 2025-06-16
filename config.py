"""
Configuration settings for NexusAI
"""
from pathlib import Path

# Assistant Configuration
WAKE_WORD = "nexus"
SPEECH_RATE = 180
SPEECH_VOLUME = 0.9

# Data Storage Configuration
DATA_DIR = Path("nexus_ai_data")
HISTORY_FILE = DATA_DIR / "conversation_history.json"
PREFERENCES_FILE = DATA_DIR / "user_preferences.json"
MEMORY_FILE = DATA_DIR / "context_memory.pickle"

# NLP Configuration
NLTK_DOWNLOADS = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
SPACY_MODEL = "en_core_web_sm"

# Intent patterns for command classification
INTENT_PATTERNS = {
    'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
    'time': ['time', 'clock', 'hour', 'minute'],
    'date': ['date', 'today', 'day', 'month', 'year'],
    'search': ['search', 'find', 'look up', 'tell me about', 'what is', 'who is'],
    'open': ['open', 'launch', 'start', 'go to'],
    'weather': ['weather', 'temperature', 'forecast', 'rain', 'sunny', 'cloudy'],
    'joke': ['joke', 'funny', 'humor', 'laugh', 'amusing'],
    'math': ['calculate', 'compute', 'add', 'subtract', 'multiply', 'divide', 'plus', 'minus'],
    'reminder': ['remind', 'remember', 'note', 'memo'],
    'question': ['what', 'how', 'why', 'when', 'where', 'who'],
    'goodbye': ['bye', 'goodbye', 'exit', 'quit', 'stop', 'end']
}

# Emotional context patterns
EMOTION_PATTERNS = {
    'positive': ['happy', 'good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic'],
    'negative': ['sad', 'bad', 'terrible', 'awful', 'horrible', 'upset', 'angry'],
    'neutral': ['okay', 'fine', 'alright', 'normal']
}

# Website shortcuts
WEBSITES = {
    'google': 'https://www.google.com',
    'youtube': 'https://www.youtube.com',
    'github': 'https://www.github.com',
    'stackoverflow': 'https://www.stackoverflow.com',
    'reddit': 'https://www.reddit.com'
}

# Jokes database
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a fake noodle? An impasta!",
    "Why did the math book look so sad? Because it had too many problems!"
]