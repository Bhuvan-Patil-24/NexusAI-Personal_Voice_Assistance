import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from textblob import TextBlob
import spacy
import difflib
from components.config import NLTK_DOWNLOADS, SPACY_MODEL, INTENT_PATTERNS, EMOTION_PATTERNS


class NLPProcessor:
    def __init__(self):
        self.setup_nlp()

    def setup_nlp(self):
        try:
            # Download NLTK data if not already present
            for item in NLTK_DOWNLOADS:
                try:
                    nltk.data.find(f'tokenizers/{item}')
                except LookupError:
                    nltk.download(item, quiet=True)
            # Initialize NLP tools
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            # Try to load spaCy model
            try:
                self.nlp = spacy.load(SPACY_MODEL)
            except OSError:
                print(
                    f"spaCy model not found. Install with: python -m spacy download {SPACY_MODEL}")
                self.nlp = None

        except Exception as e:
            print(f"NLP setup warning: {e}")

    def preprocess_text(self, text):
        # Convert to lowercase
        text = text.lower()

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords and lemmatize
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and token.isalpha():
                lemmatized = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemmatized)

        return processed_tokens

    def extract_entities(self, text):
        entities = {}

        if self.nlp:
            # Use spaCy for entity extraction
            doc = self.nlp(text)
            for ent in doc.ents:
                # Clean and normalize entity text
                entity_text = ent.text.strip().title()

                if ent.label_ not in entities:
                    entities[ent.label_] = []

                # Avoid duplicates
                if entity_text not in entities[ent.label_]:
                    entities[ent.label_].append(entity_text)
        else:
            # Fallback to NLTK
            try:
                tokens = word_tokenize(text)
                pos_tags = pos_tag(tokens)
                chunks = ne_chunk(pos_tags)

                for chunk in chunks:
                    if hasattr(chunk, 'label'):
                        entity_name = ' '.join(
                            [token for token, pos in chunk.leaves()])
                        entity_name = entity_name.strip().title()  # Clean and normalize

                        if chunk.label() not in entities:
                            entities[chunk.label()] = []

                        # Avoid duplicates
                        if entity_name not in entities[chunk.label()]:
                            entities[chunk.label()].append(entity_name)
            except Exception as e:
                print(f"Error in NLTK entity extraction: {e}")
                # Continue with empty entities if NLTK fails

        # Post-processing: Add manual entity detection for common patterns
        text_lower = text.lower()

        # Detect city names from common weather patterns
        weather_city_patterns = [
            r'(?:tell\s+me\s+the\s+)?weather\s+(?:in|for|of)\s+([a-zA-Z\s]+)',
            r'(?:tell\s+me\s+the\s+)?temperature\s+(?:in|for|of)\s+([a-zA-Z\s]+)',
            r'(?:what\s+is\s+the\s+)?weather\s+(?:in|for|of)\s+([a-zA-Z\s]+)',
            r'(?:what\s+is\s+the\s+)?temperature\s+(?:in|for|of)\s+([a-zA-Z\s]+)',
            r'(?:in|at)\s+([a-zA-Z\s]+)\s+weather',
            r'weather\s+in\s+([a-zA-Z\s]+)',
            r'weather\s+for\s+([a-zA-Z\s]+)',
            r'weather\s+of\s+([a-zA-Z\s]+)',
            r'([a-zA-Z\s]+)\s+weather'
        ]

        for pattern in weather_city_patterns:
            import re
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                city = match.strip().title()
                # Filter out common non-city words
                non_cities = ['he', 'weather', 'today', 'tell me' 'tomorrow',
                              'now', 'current', 'is', 'what', 'how', 'the', 'and']
                if city and city not in non_cities and len(city) > 1:
                    if 'GPE' not in entities:
                        entities['GPE'] = []
                    if city not in entities['GPE']:
                        entities['GPE'].append(city)

        # Detect mathematical expressions for calculation
        math_patterns = [
            r'\b\d+(?:\.\d+)?\b',  # Numbers
            r'\b(?:plus|minus|times|divide|multiply|add|subtract)\b',  # Math words
            # Number words
            r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b'
        ]

        math_found = False
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                math_found = True
                break

        if math_found:
            if 'MATH' not in entities:
                entities['MATH'] = []
            entities['MATH'].append('mathematical_expression')

        # Detect time expressions for reminders
        time_patterns = [
            r'\b(?:at|in) (\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)\b',
            r'\b(?:after|in) (\d+)\s*(?:minutes?|hours?|days?)\b',
            r'\b(?:tomorrow|today|tonight|morning|afternoon|evening)\b'
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'TIME' not in entities:
                    entities['TIME'] = []
                for match in matches:
                    time_expr = match if isinstance(
                        match, str) else ' '.join(match)
                    if time_expr not in entities['TIME']:
                        entities['TIME'].append(time_expr.strip())

        # Enhanced UI control actions and directions detection
        ui_action_patterns = {
            # Tab controls
            'switch_tab': [
                r'\b(?:switch|change|move|go)\s+(?:to\s+)?(?:the\s+)?(?:next|previous|left|right)\s+tab\b',
                r'\b(?:next|previous|left|right)\s+tab\b'
            ],
            'close_tab': [r'\bclose\s+(?:this\s+|current\s+)?tab\b'],
            'new_tab': [r'\b(?:new|open)\s+tab\b', r'\bopen\s+(?:a\s+)?new\s+tab\b'],

            # Window controls
            'close_window': [r'\bclose\s+(?:this\s+|current\s+)?window\b'],
            'minimize_window': [r'\bminimize\s+(?:this\s+|current\s+)?window\b'],
            'maximize_window': [r'\bmaximize\s+(?:this\s+|current\s+)?window\b'],

            # Volume controls
            'volume_up': [
                r'\b(?:increase|turn\s+up|raise)\s+(?:the\s+)?volume\b',
                r'\bvolume\s+up\b'
            ],
            'volume_down': [
                r'\b(?:decrease|turn\s+down|lower)\s+(?:the\s+)?volume\b',
                r'\bvolume\s+down\b'
            ],
            'mute': [r'\bmute\s+(?:the\s+)?(?:volume|sound|audio)\b', r'\bmute\b'],

            # Media controls
            'pause': [
                r'\bpause\b(?!\s+play)',  # pause but not "pause play"
                r'\bpause\s+(?:music|video|media|audio)\b'
            ],
            'play': [
                r'\bplay\b(?!\s+pause)',  # play but not "play pause"
                r'\bplay\s+(?:music|video|media|audio)\b',
                r'\bresume\b'
            ],
            'pause_play': [
                r'\bpause\s+play\b', r'\bplay\s+pause\b',
                r'\btoggle\s+(?:play|pause)\b'
            ],
            'next_track': [
                r'\b(?:next|skip)\s+(?:track|song|music)\b',
                r'\bskip\b(?!\s+(?:to|forward))',
                r'\bnext\s+(?:song|track)\b'
            ],
            'previous_track': [
                r'\b(?:previous|back)\s+(?:track|song|music)\b',
                r'\bprevious\s+(?:song|track)\b',
                r'\bback\s+(?:song|track)\b'
            ],

            # Screenshot
            'screenshot': [
                r'\btake\s+(?:a\s+)?screenshot\b',
                r'\bscreenshot\b',
                r'\bcapture\s+screen\b'
            ],

            # Text input and editing
            'type_text': [r'\btype\s+(.+)', r'\bwrite\s+(.+)', r'\binput\s+(.+)'],
            'copy': [r'\bcopy\b', r'\bctrl\s*c\b'],
            'paste': [r'\bpaste\b', r'\bctrl\s*v\b'],
            'select_all': [r'\bselect\s+all\b', r'\bctrl\s*a\b'],
            'undo': [r'\bundo\b', r'\bctrl\s*z\b'],
            'redo': [r'\bredo\b', r'\bctrl\s*y\b'],

            # Application and navigation
            'alt_tab': [r'\balt\s+tab\b', r'\bswitch\s+(?:app|application)\b'],
            'refresh': [r'\brefresh\b', r'\breload\b', r'\bf5\b'],
            'go_back': [r'\bgo\s+back\b', r'\bback\b', r'\bprevious\s+page\b'],
            'go_forward': [r'\bgo\s+forward\b', r'\bforward\b', r'\bnext\s+page\b']
        }

        direction_patterns = {
            'next': [r'\bnext\b', r'\bright\b'],
            'previous': [r'\bprevious\b', r'\bprev\b', r'\bleft\b', r'\bback\b']
        }

        # Check for UI actions
        for action, patterns in ui_action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if 'UI_ACTION' not in entities:
                        entities['UI_ACTION'] = []
                    if action not in entities['UI_ACTION']:
                        entities['UI_ACTION'].append(action)

        # Check for directions (for tab switching)
        for direction, patterns in direction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if 'DIRECTION' not in entities:
                        entities['DIRECTION'] = []
                    if direction not in entities['DIRECTION']:
                        entities['DIRECTION'].append(direction)

        # Extract text to type for type_text action
        type_patterns = [
            r'\btype\s+["\'](.+?)["\']',  # "type 'hello world'"
            r'\btype\s+(.+)',             # "type hello world"
            r'\bwrite\s+["\'](.+?)["\']',  # "write 'hello world'"
            r'\bwrite\s+(.+)',            # "write hello world"
            r'\binput\s+["\'](.+?)["\']',  # "input 'hello world'"
            r'\binput\s+(.+)'             # "input hello world"
        ]

        for pattern in type_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if 'TEXT_TO_TYPE' not in entities:
                    entities['TEXT_TO_TYPE'] = []
                for match in matches:
                    text_content = match.strip()
                    # Remove common ending words that might be captured
                    ending_words = ['please', 'now', 'here']
                    for word in ending_words:
                        if text_content.endswith(' ' + word):
                            text_content = text_content[:-len(' ' + word)]
                    if text_content and text_content not in entities['TEXT_TO_TYPE']:
                        entities['TEXT_TO_TYPE'].append(text_content)

        # Clean up empty entity lists
        entities = {k: v for k, v in entities.items() if v}

        return entities

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        sentiment = blob.sentiment

        if sentiment.polarity > 0.1:
            return 'positive'
        elif sentiment.polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'

    def classify_intent(self, text):
        text_lower = text.lower()
        tokens = self.preprocess_text(text)

        # Score each intent based on keyword matching
        intent_scores = {}
        for intent, patterns in INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 2
                # Check for partial matches in tokens
                for token in tokens:
                    if difflib.SequenceMatcher(None, token, pattern).ratio() > 0.8:
                        score += 1
            intent_scores[intent] = score

        # Return the intent with highest score
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent

        return 'unknown'

    def extract_parameters(self, text, intent):
        entities = self.extract_entities(text)
        params = {}

        if intent == 'search':
            # For search, extract the query after common search terms
            search_terms = ['search for', 'tell me about',
                            'what is', 'who is', 'find']
            query = text.lower()
            for term in search_terms:
                if term in query:
                    params['query'] = query.split(term, 1)[1].strip()
                    break
            if 'query' not in params:
                # Remove common words and use remaining as query
                tokens = self.preprocess_text(text)
                params['query'] = ' '.join(tokens)

        elif intent == 'open':
            # Extract website/application name
            text_lower = text.lower().replace('open', '').strip()
            params['target'] = text_lower

        elif intent == 'weather':
            # Extract city name from weather requests
            text_lower = text.lower()

            # Remove common weather phrases
            weather_phrases = [
                'weather', 'weather in', 'weather for', 'weather of',
                'what is the weather', 'what\'s the weather', 'how is the weather',
                'tell me the weather', 'get weather', 'show weather',
                'check weather', 'temperature', 'temperature in', 'temperature of'
            ]

            city_text = text_lower
            for phrase in weather_phrases:
                city_text = city_text.replace(phrase, '').strip()

            # Remove common prepositions and articles
            remove_words = ['in', 'for', 'of', 'at', 'the',
                            'a', 'an', 'today', 'now', 'currently']
            words = city_text.split()
            filtered_words = [
                word for word in words if word not in remove_words]

            if filtered_words:
                city = ' '.join(filtered_words).strip()
                if city:  # Make sure we have something left
                    params['city'] = city
                    # Also add as location for flexibility
                    params['location'] = city

            # Also check if entities contain location information
            if entities and 'GPE' in entities:
                # GPE (Geopolitical Entity) often contains city/country names
                if not params.get('city'):
                    params['city'] = entities['GPE'][0] if entities['GPE'] else None
                    params['location'] = params['city']

        elif intent == 'math':
            # Extract mathematical expression - improved to handle spoken math
            # Look for the entire text as potential math expression
            math_text = text.lower()

            # Remove common calculation phrases
            calc_phrases = ['calculate', 'what is',
                            'what\'s', 'compute', 'solve', 'find']
            for phrase in calc_phrases:
                math_text = math_text.replace(phrase, '').strip()

            if math_text:
                params['expression'] = math_text

        elif intent == 'reminder':
            # Extract reminder text and time if present
            reminder_text = text.lower().replace(
                'remind me', '').replace('remember', '').strip()
            params['reminder_text'] = reminder_text

        elif intent == 'ui_control':
            # Extract UI control action and parameters
            text_lower = text.lower()

            # Extract action from entities
            if 'UI_ACTION' in entities and entities['UI_ACTION']:
                params['action'] = entities['UI_ACTION'][0]

            # Extract direction for tab switching
            if 'DIRECTION' in entities and entities['DIRECTION']:
                params['direction'] = entities['DIRECTION'][0]

            # Extract text to type
            if 'TEXT_TO_TYPE' in entities and entities['TEXT_TO_TYPE']:
                params['text'] = entities['TEXT_TO_TYPE'][0]

            # Additional parameter extraction for specific actions
            if params.get('action') == 'switch_tab':
                # Ensure we have a direction for tab switching
                if not params.get('direction'):
                    if any(word in text_lower for word in ['next', 'right']):
                        params['direction'] = 'next'
                    elif any(word in text_lower for word in ['previous', 'prev', 'left', 'back']):
                        params['direction'] = 'previous'
                    else:
                        params['direction'] = 'next'  # Default to next

            elif params.get('action') == 'type_text':
                # If no text extracted from entities, try manual extraction
                if not params.get('text'):
                    type_keywords = ['type', 'write', 'input']
                    for keyword in type_keywords:
                        if keyword in text_lower:
                            # Extract everything after the keyword
                            parts = text_lower.split(keyword, 1)
                            if len(parts) > 1:
                                text_to_type = parts[1].strip()
                                # Remove common words at the beginning
                                remove_start = [
                                    'the', 'this', 'text', 'message']
                                for word in remove_start:
                                    if text_to_type.startswith(word + ' '):
                                        text_to_type = text_to_type[len(
                                            word + ' '):]
                                if text_to_type:
                                    params['text'] = text_to_type
                                break

            # Handle media control actions
            elif params.get('action') in ['pause', 'play', 'pause_play', 'next_track', 'previous_track']:
                # These actions don't need additional parameters
                pass

        # Add extracted entities
        params['entities'] = entities

        return params

    def get_fuzzy_matches(self, command):
        all_patterns = []
        for intent_patterns in INTENT_PATTERNS.values():
            all_patterns.extend(intent_patterns)

        close_matches = difflib.get_close_matches(
            command, all_patterns, n=1, cutoff=0.6)
        return close_matches
