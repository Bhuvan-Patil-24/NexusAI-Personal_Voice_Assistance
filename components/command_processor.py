import datetime
import wikipedia
import webbrowser
import random
import re
import winsound
from components.config import WAKE_WORD, WEBSITES, JOKES, APPS
from components.appLauncher import WindowsAppLauncher
from reminders.reminder_sys import ReminderSystem
from components.summarizer import GeminiSummarizer
from components.audio_handler import AudioHandler


class CommandProcessor:
    def __init__(self, nlp_processor, data_manager):
        self.nlp_processor = nlp_processor
        self.data_manager = data_manager
        self.app_launcher = WindowsAppLauncher()
        self.reminder_system = ReminderSystem()
        self.summarizer = GeminiSummarizer()
        self.audio_handler = AudioHandler()

        if self.audio_handler:
            self.reminder_system.set_reminder_callback(
                self._handle_reminder_trigger)

    def _handle_reminder_trigger(self, reminder_message):
        """Handle when a reminder is triggered"""
        print(reminder_message)
        if self.audio_handler:
            winsound.Beep(1000, 1000)  # frequency=1000Hz, duration=500ms
            # Use your existing audio handler to speak the reminder
            self.audio_handler.speak(reminder_message)

    def get_current_time(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}"

    def get_current_date(self):
        today = datetime.date.today()
        date_str = today.strftime("%B %d, %Y")
        return f"Today is {date_str}"

    def search_for(self, query):
        try:
            # Get summary from Wikipedia
            result = wikipedia.summary(query, sentences=1)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            # If there are multiple results, pick the first one
            try:
                result = wikipedia.summary(e.options[0], sentences=1)
                return result
            except:
                return "I am not able to find anything on wikepedia on that topic."
        except Exception as e:
            result = self.summarizer.summarize(query)
            if result:
                return result
            else:
                return "I couldn't find specific information about that topic."

    def open_app_or_site(self, name):
        if name in WEBSITES:
            webbrowser.open(WEBSITES[name])
            return f"Opening {name.title()}"
        elif name in APPS:
            self.app_launcher.open_app(APPS[name])
            return f"Opening {name.title()}"
        elif self.app_launcher.open_app(name):
            return f"Opening {name.title()}"
        else:
            # Try to open as a general search
            webbrowser.open(f"https://www.google.com/search?q={name}")
            return f"Searching for {name} on Google"

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
            return f"The answer is {result}"
        except:
            return self.summarizer.calculate(expression)

    def process_reminder_command(self, command, params):
        """Process reminder-related commands using the reminder system"""
        command_lower = command.lower()

        # Handle different reminder command patterns
        if any(phrase in command_lower for phrase in ['remind me to', 'set reminder to', 'remember to']):
            # Try to extract reminder text and time from params first
            reminder_text = params.get('reminder_text', '')
            time_str = params.get('time', '')

            # If not in params, use the reminder system's natural language processing
            if not reminder_text or not time_str:
                success, response = self.reminder_system.process_reminder(
                    command)
                return response
            else:
                success, response = self.reminder_system.add_reminder(
                    reminder_text, time_str)
                return response

        elif any(phrase in command_lower for phrase in ['list reminders', 'show reminders', 'my reminders']):
            return self.reminder_system.list_reminders()

        elif 'cancel reminder' in command_lower or 'delete reminder' in command_lower:
            # Extract reminder ID if possible
            words = command_lower.split()
            try:
                for word in words:
                    if word.isdigit():
                        reminder_id = int(word)
                        success, response = self.reminder_system.cancel_reminder(
                            reminder_id)
                        return response
                return "Please specify which reminder to cancel by its number."
            except:
                return "Please specify the reminder number to cancel."

        else:
            # Use the reminder system's natural language processing
            success, response = self.reminder_system.process_reminder(
                command)
            return response

    def cleanup(self):
        """Cleanup method to properly close reminder system"""
        if hasattr(self, 'reminder_system'):
            self.reminder_system.cleanup()

    def smart_search(self, query, entities):
        # If entities are detected, use them to improve search
        if entities:
            if 'PERSON' in entities:
                query = f"{query} person biography"
            elif 'GPE' in entities:  # Geopolitical entity (places)
                query = f"{query} location geography"
            elif 'ORG' in entities:  # Organization
                query = f"{query} organization company"

        return self.search_for(query)

    def handle_follow_up(self, text):
        if 'last_intent' in self.data_manager.context_memory:
            last_intent = self.data_manager.context_memory['last_intent']
            last_params = self.data_manager.context_memory.get('last_params', {})

        # Define follow-up trigger words
        follow_up_words = ['more', 'tell me more', 'continue', 'explain', 'details']

        # Check if input matches any follow-up pattern
        if any(word in text.lower() for word in follow_up_words):
            # Handle follow-up for a search
            if last_intent == 'search':
                last_query = last_params.get('query', '')
                if last_query:
                    extra_info = self.search_for(last_query)
                    return extra_info, True
                else:
                    return "I don't have the previous search query to continue.", True
            else:
                return "I'm not sure how to provide more details about that.", True

        # If no follow-up detected
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
        tone_prefix = self.generate_contextual_response(
            intent, params, sentiment)

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
            response = self.open_app_or_site(target)

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
                time_greeting = "Good morning!"
            elif hour < 17:
                time_greeting = "Good afternoon!"
            else:
                time_greeting = "Good evening!"

            if sentiment == 'positive':
                response = f"{time_greeting}! You seem to be in a great mood today. How can I help you?"
            elif sentiment == 'negative':
                response = f"{time_greeting}. I hope I can help brighten your day. What can I do for you?"
            else:
                response = f"{time_greeting}! How can I assist you today?"
            return response, False

        elif intent == 'reminder':
            response = self.process_reminder_command(original_command, params)

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
                query = command.replace('what is', '').replace(
                    'who is', '').replace('how', '').strip()
                response = self.smart_search(query, entities)
            else:
                return self.search_for(command), False

        elif intent == 'intro':
            response = "My name is Nexus, your personal voice assistant. I can help you with simple but time consuming tasks, provide information, seting reminders and much more to enhance your productivity."
            return response, False

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
        self.data_manager.learn_from_interaction(
            original_command, final_response, sentiment, self.nlp_processor)

        return final_response, False
