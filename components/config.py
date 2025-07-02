from pathlib import Path


SPEECH_RATE = 180
SPEECH_VOLUME = 1.0

# Data Storage Configuration
DATA_DIR = Path("nexus_ai_data")
HISTORY_FILE = DATA_DIR / "conversation_history.json"
PREFERENCES_FILE = DATA_DIR / "user_preferences.json"
MEMORY_FILE = DATA_DIR / "context_memory.pickle"

# NLP Configuration
NLTK_DOWNLOADS = ['punkt', 'punkt_tab', 'stopwords', 'wordnet',
                  'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
SPACY_MODEL = "en_core_web_sm"

# Intent patterns for command classification
INTENT_PATTERNS = {
    'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'wake up'],
    'time': ['time', 'clock'],
    'date': ['date', 'today', 'day', 'month', 'year'],
    'search': ['search', 'find', 'look up', 'tell me about'],
    'open': ['open', 'launch', 'start', 'go to'],
    'weather': ['weather', 'temperature', 'forecast'],
    'joke': ['joke', 'funny', 'humor', 'laugh', 'amusing'],
    'math': ['calculate', 'compute', 'add', 'subtract', 'multiply', 'divide', 'plus', 'minus'],
    'reminder': ['remind', 'remember', 'note', 'memo'],
    'question': ['what', 'how', 'why', 'when', 'where', 'who'],
    'goodbye': ['bye', 'goodbye', 'exit', 'quit', 'stop', 'end', 'see you', 'talk later', 'shut down', 'power off'],
    'intro': ['who are you', 'your name', 'introduce yourself', 'what can you do'],
    'compose': ['compose an email', 'compose mail', 'send mail', 'send email'],
    'ui_control': [
        # Tab control
        'switch tab', 'change tab', 'next tab', 'previous tab', 'left tab', 'right tab',
        'close tab', 'close this tab', 'close current tab',
        'new tab', 'open tab', 'open new tab', 'create tab',

        # Window control
        'close window', 'close this window', 'close current window',
        'minimize window', 'minimise this window', 'minimise current window',
        'maximize window', 'maximise this window', 'maximise current window',
        # Volume control
        'volume up', 'increase volume', 'turn up volume', 'raise volume',
        'volume down', 'decrease volume', 'turn down volume', 'lower volume',
        'mute', 'mute volume', 'mute sound', 'mute audio', 'unmute',

        # Media control
        'pause', 'pause music', 'pause video', 'pause media', 'pause audio',
        'play', 'play music', 'play video', 'play media', 'resume',
        'pause play', 'play pause', 'toggle play', 'toggle pause',
        'next track', 'next song', 'skip', 'skip song', 'next music',
        'previous track', 'previous song', 'back track', 'back song', 'last song',
        'stop music', 'stop audio', 'stop video', 'stop media',

        # Screenshot
        'screenshot', 'take screenshot', 'capture screen', 'screen capture',

        # Text input and editing
        'type', 'write', 'input', 'enter text', 'type text',
        'copy', 'copy text', 'ctrl c',
        'paste', 'paste text', 'ctrl v',
        'select all', 'ctrl a', 'select everything',
        'undo', 'ctrl z', 'undo last', 'undo action',
        'redo', 'ctrl y', 'redo last', 'redo action',

        # Application switching
        'alt tab', 'switch app', 'switch application', 'change app',

        # Browser navigation
        'refresh', 'reload', 'refresh page', 'reload page', 'f5',
        'go back', 'back', 'previous page', 'navigate back',
        'go forward', 'forward', 'next page', 'navigate forward',

        # General actions
        'press key', 'hit key', 'click key'
    ]
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

# Daily use apps
APPS = {
    'calculator': 'calc',
    'powershell': 'cmd',
    'vscode': 'code',
    'vs code': 'code',
    'edge': 'msedge',
    'powerpoint': 'powerpnt'
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