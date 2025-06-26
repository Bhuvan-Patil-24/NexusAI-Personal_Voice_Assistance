import datetime
import wikipedia
import webbrowser
import random
import re
from config import WAKE_WORD, WEBSITES, JOKES

class CommandProcessor:
    def __init__(self, nlp_processor, data_manager):
        self.nlp_processor = nlp_processor
        self.data_manager = data_manager
    
    def get_current_time(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"Sir, The current time is {time_str}"
    
    def get_current_date(self):
        today = datetime.date.today()
        date_str = today.strftime("%B %d, %Y")
        return f"Sir, Today is {date_str}"
    
    def search_wikipedia(self, query):
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
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return "I couldn't find information about that topic on Wikipedia."
    
    def open_website(self, site):
        if site in WEBSITES:
            webbrowser.open(WEBSITES[site])
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
        return random.choice(JOKES)
    
    def calculate_expression(self, expression):
        try:
            # Remove any non-mathematical characters for safety
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            result = eval(safe_expr)
            return f"The result is {result}"
        except:
            return "I couldn't calculate that expression. Please check your math problem."
    
    def smart_search(self, query, entities):
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
        if 'last_intent' in self.data_manager.context_memory:
            last_intent = self.data_manager.context_memory['last_intent']
            
            # Check for follow-up patterns
            follow_up_words = ['more', 'tell me more', 'continue', 'explain', 'details']
            if any(word in text.lower() for word in follow_up_words):
                if last_intent == 'search' and 'last_params' in self.data_manager.context_memory:
                    last_query = self.data_manager.context_memory['last_params'].get('query', '')
                    return f"Let me search for more information about {last_query}", True
        
        return "", False
    
    def generate_contextual_response(self, intent, params, sentiment):
        # Adjust response tone based on sentiment
        if sentiment == 'negative':
            tone_prefix = "I understand you might be feeling down. "
        elif sentiment == 'positive':
            tone_prefix = "I'm glad you're in a good mood! "
        else:
            tone_prefix = ""
        
        # Store context for follow-up questions
        self.data_manager.context_memory['last_intent'] = intent
        self.data_manager.context_memory['last_params'] = params
        self.data_manager.context_memory['last_sentiment'] = sentiment
        
        return tone_prefix
    
    def process_command(self, command):
        original_command = command
        command = command.lower()
        
        # Remove wake word if present
        if WAKE_WORD in command:
            command = command.replace(WAKE_WORD, "").strip()
        
        # Check for follow-up questions first
        follow_up_response, is_follow_up = self.handle_follow_up(command)
        if is_follow_up:
            return follow_up_response, False
        
        # Analyze sentiment and classify intent
        sentiment = self.nlp_processor.analyze_sentiment(command)
        intent = self.nlp_processor.classify_intent(command)
        params = self.nlp_processor.extract_parameters(command, intent)
        
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
            print(f"Searching for {query}...")
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
                time_greeting = "Good morning Sir!"
            elif hour < 17:
                time_greeting = "Good afternoon Sir!"
            else:
                time_greeting = "Good evening Sir!"
            
            if sentiment == 'positive':
                response = f"{time_greeting}! You seem to be in a great mood today. How can I help you?"
            elif sentiment == 'negative':
                response = f"{time_greeting}. I hope I can help brighten your day. What can I do for you?"
            else:
                response = f"{time_greeting}! How can I assist you today?"
            return response, True
        
        elif intent == 'reminder':
            reminder_text = params.get('reminder_text', '')
            if reminder_text:
                # Store reminder (in a real implementation, you'd use a database)
                response = f"I'll remember to remind you about: {reminder_text}. Note: Full reminder system requires additional setup."
            else:
                response = "What would you like me to remind you about?"
        
        elif intent == 'goodbye':
            # Personalized goodbye based on interaction history
            if len(self.data_manager.conversation_history) > 5:
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
            close_matches = self.nlp_processor.get_fuzzy_matches(command)
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
        self.data_manager.learn_from_interaction(original_command, final_response, sentiment, self.nlp_processor)
        
        return final_response, False