import datetime
import wikipedia
import webbrowser
import requests
import random
import re, math
import winsound
from components.config import WAKE_WORD, WEBSITES, JOKES, APPS, WEATHER_API_KEY
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
            for i in range(3):
                winsound.Beep(1000, 1000)  # frequency=1000Hz, duration=1000ms
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

    def get_lat_lon(self, city):
        """Get latitude and longitude for a city"""
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={WEATHER_API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            if data and len(data) > 0:
                # Return the first match (most relevant)
                return data[0]['lat'], data[0]['lon']
            else:
                return None, None
        except Exception as e:
            print("Error in get_lat_lon: ", e)
            return None, None

    def get_weather(self, city=None):
        """Get weather information for a city"""
        if not city:
            return "Please tell me which city you want the weather for."

        try:
            # Get coordinates
            coords = self.get_lat_lon(city)

            # Check if coordinates were successfully retrieved
            if coords is None or coords == (None, None):
                return f"I couldn't find the location '{city}'. Please check the city name and try again."

            lat, lon = coords

            # Check if lat and lon are valid
            if lat is None or lon is None:
                return f"I couldn't find the location '{city}'. Please check the city name and try again."

            # Get weather data
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
            res = requests.get(url)

            if res.status_code != 200:
                return "I had trouble retrieving the weather data. Please try again later."

            data = res.json()

            # Extract weather details
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            # Convert temperature from Kelvin to Celsius
            temp_celsius = round(temp - 273.15, 1)

            # Format response
            weather_report = (
                f"The current weather in {city.title()} is {desc} with a temperature of {temp_celsius}°C, "
                f"humidity at {humidity}%, and wind speed of {wind_speed} meters per second."
            )
            return weather_report

        except Exception as e:
            print("Error in get_weather: ", e)
            return "I had trouble retrieving the weather. Please try again later."

    def tell_joke(self):
        return random.choice(JOKES)

    def calculate_expression(self, expression):
        try:
            # Convert spoken words to mathematical symbols
            word_to_symbol = {
                'plus': '+', 'add': '+', 'added to': '+', 'and': '+',
                'minus': '-', 'subtract': '-', 'subtracted from': '-', 'take away': '-',
                'times': '*', 'multiply': '*', 'multiplied by': '*', 'into': '*',
                'divide': '/', 'divided by': '/', 'over': '/',
                'power': '**', 'to the power of': '**', 'raised to': '**', 'squared': '**2',
                'cubed': '**3', 'square root': 'sqrt', 'percent': '/100',
                'point': '.', 'decimal': '.', 'factorial': '!', 'factorial of': '!'
            }

            # Convert number words to digits
            number_words = {
                'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
                'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
                'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
                'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
                'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
                'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
                'eighty': '80', 'ninety': '90', 'hundred': '100', 'thousand': '1000'
            }

            # Clean and normalize the expression
            expression = expression.lower().strip()

            # Replace word numbers with digits
            for word, digit in number_words.items():
                expression = expression.replace(word, digit)

            # Replace mathematical word operators with symbols
            for word, symbol in word_to_symbol.items():
                expression = expression.replace(word, symbol)

            # Handle special cases
            # 'x' often used for multiplication
            expression = expression.replace('x', '*')
            expression = expression.replace('÷', '/')  # division symbol

            # Remove common filler words
            filler_words = ['what', 'is', 'equals', 'equal',
                            'to', 'the', 'result', 'of', 'calculate']
            for word in filler_words:
                expression = expression.replace(word, '')

            # Clean up extra spaces
            expression = ' '.join(expression.split())

            # Handle factorial expressions
            if '!' in expression:
                return self._calculate_factorial_expression(expression)

            # Remove any remaining non-mathematical characters (but keep spaces, decimals, and basic operators)
            import re
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            safe_expr = safe_expr.strip()

            # Check if we have a valid expression
            if not safe_expr or not any(char.isdigit() for char in safe_expr):
                raise ValueError("No valid mathematical expression found")

            # Handle simple cases where there might be missing operators
            # e.g., "5 5" should be "5 * 5" or "5 + 5" - we'll assume multiplication
            parts = safe_expr.split()
            if len(parts) == 2 and all(part.replace('.', '').isdigit() for part in parts):
                safe_expr = f"{parts[0]} * {parts[1]}"

            # Handle square root
            if 'sqrt' in expression:
                safe_expr = self._handle_sqrt(safe_expr)

            # Evaluate the expression
            result = eval(safe_expr)

            # Format the result nicely
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)  # Round to 6 decimal places

            return f"The answer is {result}"

        except:
            # If conversion fails, try the summarizer as fallback
            return self.summarizer.calculate(expression)

    def _calculate_factorial_expression(self, expression):
        try:
            # Find all factorial patterns like "5!" or "number!"
            factorial_pattern = r'(\d+)!'

            # Replace all factorials with their calculated values
            def replace_factorial(match):
                num = int(match.group(1))
                if num < 0:
                    raise ValueError(
                        "Factorial is not defined for negative numbers")
                if num > 170:  # Prevent overflow
                    raise ValueError(
                        "Number too large for factorial calculation")
                return str(math.factorial(num))

            # Replace factorials in the expression
            processed_expr = re.sub(
                factorial_pattern, replace_factorial, expression)

            # Now evaluate the rest of the expression normally
            safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', processed_expr)
            safe_expr = safe_expr.strip()

            if safe_expr:
                result = eval(safe_expr)
            else:
                # If it's just a single factorial
                factorial_match = re.search(r'(\d+)!', expression)
                if factorial_match:
                    num = int(factorial_match.group(1))
                    result = math.factorial(num)
                else:
                    raise ValueError("Invalid factorial expression")

            # Format the result
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            return f"The answer is {result}"

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception:
            return "I couldn't calculate that factorial expression."

    def _handle_sqrt(self, expression):
        # This is a simple implementation - you can expand it
        # For now, it handles basic sqrt cases
        sqrt_pattern = r'sqrt\((\d+(?:\.\d+)?)\)'

        def replace_sqrt(match):
            num = float(match.group(1))
            return str(math.sqrt(num))

        return re.sub(sqrt_pattern, replace_sqrt, expression)

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
            # Check if entities contain actual values (not just entity types)
            if 'PERSON' in entities and entities['PERSON']:
                # Use the person's name from entities for more accurate search
                person_name = entities['PERSON'][0] if isinstance(
                    entities['PERSON'], list) else entities['PERSON']
                query = f"{person_name} biography"
            # Geopolitical entity (places)
            elif 'GPE' in entities and entities['GPE']:
                # Use the place name from entities
                place_name = entities['GPE'][0] if isinstance(
                    entities['GPE'], list) else entities['GPE']
                query = f"{place_name} location geography information"
            elif 'ORG' in entities and entities['ORG']:  # Organization
                # Use the organization name from entities
                org_name = entities['ORG'][0] if isinstance(
                    entities['ORG'], list) else entities['ORG']
                query = f"{org_name} organization company information"
            elif 'MONEY' in entities and entities['MONEY']:
                # Handle money/financial queries
                query = f"{query} financial information"
            elif 'DATE' in entities and entities['DATE']:
                # Handle date-related queries
                query = f"{query} historical information"
            elif 'TIME' in entities and entities['TIME']:
                # Handle time-related queries
                query = f"{query} schedule timing information"
            else:
                # If entities exist but don't match specific types, enhance the original query
                # Extract the first available entity value
                for entity_type, entity_values in entities.items():
                    if entity_values:
                        entity_value = entity_values[0] if isinstance(
                            entity_values, list) else entity_values
                        query = f"{entity_value} {query}".strip()
                        break

        # Clean up the query - remove duplicate words and extra spaces
        query_words = query.split()
        seen = set()
        cleaned_query = []
        for word in query_words:
            word_lower = word.lower()
            if word_lower not in seen:
                seen.add(word_lower)
                cleaned_query.append(word)

        final_query = ' '.join(cleaned_query)

        return self.search_for(final_query)

    def handle_follow_up(self, text):
        if 'last_intent' in self.data_manager.context_memory:
            last_intent = self.data_manager.context_memory['last_intent']
            last_params = self.data_manager.context_memory.get(
                'last_params', {})

        # Define follow-up trigger words
        follow_up_words = ['more', 'tell me more',
                           'continue', 'explain', 'details']

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
            city = params.get('city', params.get('location', None))

            response = self.get_weather(city)

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
