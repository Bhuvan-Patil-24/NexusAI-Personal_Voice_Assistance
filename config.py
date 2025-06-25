from pathlib import Path

# Assistant Configuration
WAKE_WORD = "nexus"
SPEECH_RATE = 180
SPEECH_VOLUME = 1.0

# Data Storage Configuration
DATA_DIR = Path("nexus_ai_data")
HISTORY_FILE = DATA_DIR / "conversation_history.json"
PREFERENCES_FILE = DATA_DIR / "user_preferences.json"
MEMORY_FILE = DATA_DIR / "context_memory.pickle"

# NLP Configuration
NLTK_DOWNLOADS = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
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
    'goodbye': ['bye', 'goodbye', 'exit', 'quit', 'stop', 'end', 'see you', 'talk later', 'shut down'],
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
    'reddit': 'https://www.reddit.com',
    'wikipedia': 'https://www.wikipedia.org'
}

# Jokes database
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why did the chicken cross the road? To get to the other side!",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call a fake noodle? An impasta!",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "Why did the math book look so sad? Because it had too many problems!"
]

# API Keys
GEMINI_API_KEY = "AIzaSyA01Il4_89uEM9CRFeSnTfRz2MCfmLIFMY"
