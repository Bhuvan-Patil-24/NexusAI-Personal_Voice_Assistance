import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from textblob import TextBlob
import spacy
import difflib
import re
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
                print(f"spaCy model not found. Install with: python -m spacy download {SPACY_MODEL}")
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
                        entity_name = ' '.join([token for token, pos in chunk.leaves()])
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
            r'weather (?:in|for|of) ([a-zA-Z\s]+)',
            r'temperature (?:in|of) ([a-zA-Z\s]+)',
            r'(?:in|at) ([a-zA-Z\s]+) weather',
            r'([a-zA-Z\s]+) weather'
        ]
        
        for pattern in weather_city_patterns:
            import re
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                city = match.strip().title()
                # Filter out common non-city words
                non_cities = ['The', 'Weather', 'Today', 'Tomorrow', 'Now', 'Current', 'Is', 'What', 'How']
                if city and city not in non_cities and len(city) > 1:
                    if 'GPE' not in entities:
                        entities['GPE'] = []
                    if city not in entities['GPE']:
                        entities['GPE'].append(city)
        
        # Detect mathematical expressions for calculation
        math_patterns = [
            r'\b\d+(?:\.\d+)?\b',  # Numbers
            r'\b(?:plus|minus|times|divide|multiply|add|subtract)\b',  # Math words
            r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b'  # Number words
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
                    time_expr = match if isinstance(match, str) else ' '.join(match)
                    if time_expr not in entities['TIME']:
                        entities['TIME'].append(time_expr.strip())
        
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
            search_terms = ['search for', 'tell me about', 'what is', 'who is', 'find']
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
            remove_words = ['in', 'for', 'of', 'at', 'the', 'a', 'an', 'today', 'now', 'currently']
            words = city_text.split()
            filtered_words = [word for word in words if word not in remove_words]
            
            if filtered_words:
                city = ' '.join(filtered_words).strip()
                if city:  # Make sure we have something left
                    params['city'] = city
                    params['location'] = city  # Also add as location for flexibility
            
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
            calc_phrases = ['calculate', 'what is', 'what\'s', 'compute', 'solve', 'find']
            for phrase in calc_phrases:
                math_text = math_text.replace(phrase, '').strip()
            
            if math_text:
                params['expression'] = math_text
        
        elif intent == 'reminder':
            # Extract reminder text and time if present
            reminder_text = text.lower().replace('remind me', '').replace('remember', '').strip()
            params['reminder_text'] = reminder_text
        
        # Add extracted entities
        params['entities'] = entities
        
        return params
    
    def get_fuzzy_matches(self, command):
        all_patterns = []
        for intent_patterns in INTENT_PATTERNS.values():
            all_patterns.extend(intent_patterns)
        
        close_matches = difflib.get_close_matches(command, all_patterns, n=1, cutoff=0.6)
        return close_matches