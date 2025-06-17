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
from config import NLTK_DOWNLOADS, SPACY_MODEL, INTENT_PATTERNS, EMOTION_PATTERNS

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
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
        else:
            # Fallback to NLTK
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            chunks = ne_chunk(pos_tags)
            
            for chunk in chunks:
                if hasattr(chunk, 'label'):
                    entity_name = ' '.join([token for token, pos in chunk.leaves()])
                    if chunk.label() not in entities:
                        entities[chunk.label()] = []
                    entities[chunk.label()].append(entity_name)
        
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
        
        elif intent == 'math':
            # Extract mathematical expression
            # Simple regex to find numbers and operators
            math_pattern = r'[\d+\-*/().\s]+'
            match = re.search(math_pattern, text)
            if match:
                params['expression'] = match.group().strip()
        
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