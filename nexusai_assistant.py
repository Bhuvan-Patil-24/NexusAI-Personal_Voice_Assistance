import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import random
import requests
import json
from threading import Thread
import time
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from textblob import TextBlob
import spacy
from collections import Counter
import difflib
import pickle
from pathlib import Path

class NexusAI:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        
        # Assistant state
        self.is_listening = False
        self.wake_word = "nexus"
        
        # Initialize NLP components
        self.setup_nlp()
        
        # Create data directory for persistent storage
        self.data_dir = Path("nexus_ai_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths for persistent storage
        self.history_file = self.data_dir / "conversation_history.json"
        self.preferences_file = self.data_dir / "user_preferences.json"
        self.memory_file = self.data_dir / "context_memory.pickle"
        
        # Load existing data or initialize
        self.conversation_history = self.load_conversation_history()
        self.user_preferences = self.load_user_preferences()
        self.context_memory = self.load_context_memory()
        
        # Greet user on startup
        self.speak("Hello! I'm NexusAI, your personal voice assistant with advanced natural language processing. Say 'Nexus' followed by your command to wake me up.")
        
    def setup_nlp(self):
        """Initialize NLP components and download required data"""
        try:
            # Download NLTK data if not already present
            nltk_downloads = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
            for item in nltk_downloads:
                try:
                    nltk.data.find(f'tokenizers/{item}')
                except LookupError:
                    nltk.download(item, quiet=True)
            
            # Initialize NLP tools
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Try to load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            # Intent patterns for command classification
            self.intent_patterns = {
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
            self.emotion_patterns = {
                'positive': ['happy', 'good', 'great', 'excellent', 'wonderful', 'amazing', 'fantastic'],
                'negative': ['sad', 'bad', 'terrible', 'awful', 'horrible', 'upset', 'angry'],
                'neutral': ['okay', 'fine', 'alright', 'normal']
            }
            
        except Exception as e:
            print(f"NLP setup warning: {e}")
    
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Convert timestamp strings back to datetime objects
                for item in data:
                    if 'timestamp' in item:
                        item['timestamp'] = datetime.datetime.fromisoformat(item['timestamp'])
                print(f"Loaded {len(data)} previous conversations")
                return data
        except Exception as e:
            print(f"Could not load conversation history: {e}")
        return []
    
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data_to_save = []
            for item in self.conversation_history:
                item_copy = item.copy()
                if 'timestamp' in item_copy:
                    item_copy['timestamp'] = item_copy['timestamp'].isoformat()
                data_to_save.append(item_copy)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save conversation history: {e}")
    
    def load_user_preferences(self):
        """Load user preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Loaded {len(data)} user preferences")
                return data
        except Exception as e:
            print(f"Could not load user preferences: {e}")
        return {}
    
    def save_user_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save user preferences: {e}")
    
    def load_context_memory(self):
        """Load context memory from file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'rb') as f:
                    data = pickle.load(f)
                print("Loaded previous context memory")
                return data
        except Exception as e:
            print(f"Could not load context memory: {e}")
        return {}
    
    def save_context_memory(self):
        """Save context memory to file"""
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.context_memory, f)
        except Exception as e:
            print(f"Could not save context memory: {e}")
    
    def get_storage_info(self):
        """Get information about stored data"""
        info = {
            'conversation_count': len(self.conversation_history),
            'preferences_count': len(self.user_preferences),
            'storage_location': str(self.data_dir.absolute()),
            'files': {
                'history': str(self.history_file.name) if self.history_file.exists() else "Not created yet",
                'preferences': str(self.preferences_file.name) if self.preferences_file.exists() else "Not created yet",
                'memory': str(self.memory_file.name) if self.memory_file.exists() else "Not created yet"
            }
        }
        return info
    
    def clear_all_data(self):
        """Clear all stored data (useful for privacy)"""
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            if self.preferences_file.exists():
                self.preferences_file.unlink()
            if self.memory_file.exists():
                self.memory_file.unlink()
            
            # Reset in-memory data
            self.conversation_history = []
            self.user_preferences = {}
            self.context_memory = {}
            
            return "All stored data has been cleared successfully."
        except Exception as e:
            return f"Error clearing data: {e}"
    
    def get_user_stats(self):
        """Get statistics about user interactions"""
        if not self.conversation_history:
            return "No conversation data available yet."
        
        total_conversations = len(self.conversation_history)
        
        # Sentiment analysis of conversations
        sentiments = [item.get('sentiment', 'neutral') for item in self.conversation_history]
        sentiment_counts = Counter(sentiments)
        
        # Most common preferences
        top_preferences = Counter(self.user_preferences).most_common(5)
        
        # First and last interaction
        first_interaction = self.conversation_history[0]['timestamp'].strftime("%Y-%m-%d %H:%M")
        last_interaction = self.conversation_history[-1]['timestamp'].strftime("%Y-%m-%d %H:%M")
        
        stats = f"""
        📊 Your NexusAI Usage Statistics:
        
        🗣️ Total Conversations: {total_conversations}
        📅 First Interaction: {first_interaction}
        📅 Last Interaction: {last_interaction}
        
        😊 Mood Analysis:
        • Positive: {sentiment_counts.get('positive', 0)}
        • Neutral: {sentiment_counts.get('neutral', 0)}
        • Negative: {sentiment_counts.get('negative', 0)}
        
        🔤 Top Topics You Ask About:
        """
        
        for word, count in top_preferences:
            stats += f"• {word}: {count} times\n        "
        
        return stats.strip()
    
    def preprocess_text(self, text):
        """Advanced text preprocessing using NLP"""
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
        """Extract named entities from text"""
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
        """Analyze sentiment of the text"""
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        if sentiment.polarity > 0.1:
            return 'positive'
        elif sentiment.polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def classify_intent(self, text):
        """Classify the intent of user input using NLP"""
        text_lower = text.lower()
        tokens = self.preprocess_text(text)
        
        # Score each intent based on keyword matching
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
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
        """Extract parameters from text based on intent"""
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
    
    def generate_contextual_response(self, intent, params, sentiment):
        """Generate contextual responses based on NLP analysis"""
        # Adjust response tone based on sentiment
        if sentiment == 'negative':
            tone_prefix = "I understand you might be feeling down. "
        elif sentiment == 'positive':
            tone_prefix = "I'm glad you're in a good mood! "
        else:
            tone_prefix = ""
        
        # Store context for follow-up questions
        self.context_memory['last_intent'] = intent
        self.context_memory['last_params'] = params
        self.context_memory['last_sentiment'] = sentiment
        
        return tone_prefix
    
    def calculate_expression(self, expression):
        """Safely calculate mathematical expressions"""
        try:
            # Remove any non-mathematical characters for safety
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(safe_expr)
            return f"The result is {result}"
        except:
            return "I couldn't calculate that expression. Please check your math problem."
    
    def smart_search(self, query, entities):
        """Enhanced search using NLP insights"""
        # If entities are detected, use them to improve search
        if entities:
            if 'PERSON' in entities:
                query = f"{query} person biography"
            elif 'GPE' in entities:  # Geopolitical entity (places)
                query = f"{query} location geography"
            elif 'ORG' in entities:  # Organization
                query = f"{query} organization company"
        
        return self.search_wikipedia(query)
    
    def handle_follow_up(self, text):
        """Handle follow-up questions based on context"""
        if 'last_intent' in self.context_memory:
            last_intent = self.context_memory['last_intent']
            
            # Check for follow-up patterns
            follow_up_words = ['more', 'tell me more', 'continue', 'explain', 'details']
            if any(word in text.lower() for word in follow_up_words):
                if last_intent == 'search' and 'last_params' in self.context_memory:
                    last_query = self.context_memory['last_params'].get('query', '')
                    return f"Let me search for more information about {last_query}", True
        
        return "", False
    
    def learn_from_interaction(self, user_input, response):
        """Learn from user interactions to improve responses"""
        # Store conversation history
        self.conversation_history.append({
            'timestamp': datetime.datetime.now(),
            'user_input': user_input,
            'response': response,
            'sentiment': self.analyze_sentiment(user_input)
        })
        
        # Keep only last 100 interactions in memory (but save all to file)
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        # Extract user preferences
        tokens = self.preprocess_text(user_input)
        for token in tokens:
            if token in self.user_preferences:
                self.user_preferences[token] += 1
            else:
                self.user_preferences[token] = 1
        
        # Save to persistent storage
        self.save_conversation_history()
        self.save_user_preferences()
        self.save_context_memory()
        """Configure the text-to-speech voice"""
        voices = self.tts_engine.getProperty('voices')
        # Try to set a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"NexusAI: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        """Listen for audio input and convert to text"""
        try:
            with self.microphone as source:
                print("Listening...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Convert audio to text
            text = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
            
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            self.speak("Sorry, I'm having trouble with speech recognition right now.")
            return ""
        except sr.WaitTimeoutError:
            return ""
    
    def get_current_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}"
    
    def get_current_date(self):
        """Get current date"""
        today = datetime.date.today()
        date_str = today.strftime("%B %d, %Y")
        return f"Today is {date_str}"
    
    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            # Get summary from Wikipedia
            result = wikipedia.summary(query, sentences=2)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            # If there are multiple results, pick the first one
            try:
                result = wikipedia.summary(e.options[0], sentences=2)
                return result
            except:
                return "I couldn't find specific information about that topic."
        except:
            return "I couldn't find information about that topic on Wikipedia."
    
    def open_website(self, site):
        """Open websites"""
        sites = {
            'google': 'https://www.google.com',
            'youtube': 'https://www.youtube.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://www.stackoverflow.com',
            'reddit': 'https://www.reddit.com'
        }
        
        if site in sites:
            webbrowser.open(sites[site])
            return f"Opening {site.title()}"
        else:
            # Try to open as a general search
            webbrowser.open(f"https://www.google.com/search?q={site}")
            return f"Searching for {site} on Google"
    
    def get_weather(self, city=""):
        """Get weather information (requires API key)"""
        # This is a placeholder - you'll need to sign up for a weather API
        return "Weather feature requires an API key. Please set up OpenWeatherMap API for weather updates."
    
    def tell_joke(self):
        """Tell a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        return random.choice(jokes)
    
    def process_command(self, command):
        """Enhanced command processing with NLP"""
        original_command = command
        command = command.lower()
        
        # Remove wake word if present
        if self.wake_word in command:
            command = command.replace(self.wake_word, "").strip()
        
        # Check for follow-up questions first
        follow_up_response, is_follow_up = self.handle_follow_up(command)
        if is_follow_up:
            return follow_up_response, False
        
        # Analyze sentiment and classify intent
        sentiment = self.analyze_sentiment(command)
        intent = self.classify_intent(command)
        params = self.extract_parameters(command, intent)
        
        # Generate contextual response prefix
        tone_prefix = self.generate_contextual_response(intent, params, sentiment)
        
        # Process based on classified intent
        if intent == 'time':
            response = self.get_current_time()
        
        elif intent == 'date':
            response = self.get_current_date()
        
        elif intent == 'search':
            query = params.get('query', 'general information')
            entities = params.get('entities', {})
            self.speak(f"Searching for information about {query}")
            response = self.smart_search(query, entities)
        
        elif intent == 'open':
            target = params.get('target', 'google')
            response = self.open_website(target)
        
        elif intent == 'weather':
            response = self.get_weather()
        
        elif intent == 'joke':
            response = self.tell_joke()
        
        elif intent == 'math':
            if 'expression' in params:
                response = self.calculate_expression(params['expression'])
            else:
                response = "Please provide a mathematical expression to calculate."
        
        elif intent == 'greeting':
            # Personalized greeting based on time and sentiment
            hour = datetime.datetime.now().hour
            if hour < 12:
                time_greeting = "Good morning"
            elif hour < 17:
                time_greeting = "Good afternoon"
            else:
                time_greeting = "Good evening"
            
            if sentiment == 'positive':
                response = f"{time_greeting}! You seem to be in a great mood today. How can I help you?"
            elif sentiment == 'negative':
                response = f"{time_greeting}. I hope I can help brighten your day. What can I do for you?"
            else:
                response = f"{time_greeting}! How can I assist you today?"
        
        elif intent == 'reminder':
            reminder_text = params.get('reminder_text', '')
            if reminder_text:
                # Store reminder (in a real implementation, you'd use a database)
                response = f"I'll remember to remind you about: {reminder_text}. Note: Full reminder system requires additional setup."
            else:
                response = "What would you like me to remind you about?"
        
        elif intent == 'goodbye':
            # Personalized goodbye based on interaction history
            if len(self.conversation_history) > 5:
                response = "It's been great chatting with you today! Goodbye and have a wonderful day!"
            else:
                response = "Goodbye! Feel free to come back anytime for assistance."
            return tone_prefix + response, True
        
        elif intent == 'question':
            # Handle general questions intelligently
            entities = params.get('entities', {})
            if entities or len(command.split()) > 3:
                # Complex question - try to search for it
                query = command.replace('what is', '').replace('who is', '').replace('how', '').strip()
                response = self.smart_search(query, entities)
            else:
                response = "That's an interesting question. Could you be more specific so I can help you better?"
        
        # Fallback for unknown intents
        else:
            # Try to find similar commands using fuzzy matching
            all_patterns = []
            for intent_patterns in self.intent_patterns.values():
                all_patterns.extend(intent_patterns)
            
            close_matches = difflib.get_close_matches(command, all_patterns, n=1, cutoff=0.6)
            if close_matches:
                response = f"Did you mean something related to '{close_matches[0]}'? Please try rephrasing your request."
            else:
                responses = [
                    "I'm still learning! Could you rephrase that or try asking differently?",
                    "That's interesting, but I'm not sure how to help with that yet. Try asking in a different way.",
                    "I want to help, but I need a bit more context. Could you explain what you're looking for?"
                ]
                response = random.choice(responses)
        
        # Learn from this interaction
        final_response = tone_prefix + response
        self.learn_from_interaction(original_command, final_response)
        
        return final_response, False
    
    def run(self):
        """Main loop for the voice assistant"""
        self.speak("I'm ready to help! Say 'Nexus' followed by your command.")
        
        while True:
            try:
                # Listen for input
                audio_input = self.listen()
                
                if audio_input:
                    # Check if wake word is present or if we're in conversation
                    if self.wake_word in audio_input or self.is_listening:
                        # Process the command
                        response, should_exit = self.process_command(audio_input)
                        self.speak(response)
                        
                        if should_exit:
                            break
                        
                        # Set listening state for follow-up commands
                        self.is_listening = True
                        
                        # Reset listening state after a few seconds
                        def reset_listening():
                            time.sleep(10)
                            self.is_listening = False
                        
                        Thread(target=reset_listening, daemon=True).start()
                
            except KeyboardInterrupt:
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("Sorry, I encountered an error.")

def main():
    """Main function to run NexusAI with NLP capabilities"""
    try:
        print("Initializing NexusAI with Natural Language Processing...")
        print("Required packages: speechrecognition pyttsx3 wikipedia requests nltk textblob spacy")
        print("For full NLP features, also run: python -m spacy download en_core_web_sm")
        
        assistant = NexusAI()
        assistant.run()
    except Exception as e:
        print(f"Failed to start NexusAI: {e}")
        print("\nMake sure you have installed all required packages:")
        print("pip install speechrecognition pyttsx3 wikipedia requests pyaudio nltk textblob spacy")
        print("python -m spacy download en_core_web_sm")
        print("\nFor basic functionality without advanced NLP:")
        print("pip install speechrecognition pyttsx3 wikipedia requests pyaudio")

if __name__ == "__main__":
    main()