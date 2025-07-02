import json
import pickle
import datetime
from collections import Counter
from components.config import DATA_DIR, HISTORY_FILE, PREFERENCES_FILE, MEMORY_FILE

class DataManager:
    def __init__(self):
        # Create data directory for persistent storage
        DATA_DIR.mkdir(exist_ok=True)
        
        # Load existing data or initialize
        self.conversation_history = self.load_conversation_history()
        self.user_preferences = self.load_user_preferences()
        self.context_memory = self.load_context_memory()
    
    def load_conversation_history(self):
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
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
        try:
            # Convert datetime objects to strings for JSON serialization
            data_to_save = []
            for item in self.conversation_history:
                item_copy = item.copy()
                if 'timestamp' in item_copy:
                    item_copy['timestamp'] = item_copy['timestamp'].isoformat()
                data_to_save.append(item_copy)
            
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save conversation history: {e}")
    
    def load_user_preferences(self):
        try:
            if PREFERENCES_FILE.exists():
                with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Loaded {len(data)} user preferences")
                return data
        except Exception as e:
            print(f"Could not load user preferences: {e}")
        return {}
    
    def save_user_preferences(self):
        try:
            with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Could not save user preferences: {e}")
    
    def load_context_memory(self):
        try:
            if MEMORY_FILE.exists():
                with open(MEMORY_FILE, 'rb') as f:
                    data = pickle.load(f)
                print("Loaded previous context memory")
                return data
        except Exception as e:
            print(f"Could not load context memory: {e}")
        return {}
    
    def save_context_memory(self):
        try:
            with open(MEMORY_FILE, 'wb') as f:
                pickle.dump(self.context_memory, f)
        except Exception as e:
            print(f"Could not save context memory: {e}")
    
    def save_all_data(self):
        self.save_conversation_history()
        self.save_user_preferences()  
        self.save_context_memory()

    def get_storage_info(self):
        info = {
            'conversation_count': len(self.conversation_history),
            'preferences_count': len(self.user_preferences),
            'storage_location': str(DATA_DIR.absolute()),
            'files': {
                'history': str(HISTORY_FILE.name) if HISTORY_FILE.exists() else "Not created yet",
                'preferences': str(PREFERENCES_FILE.name) if PREFERENCES_FILE.exists() else "Not created yet",
                'memory': str(MEMORY_FILE.name) if MEMORY_FILE.exists() else "Not created yet"
            }
        }
        return info
    
    def clear_all_data(self):
        try:
            if HISTORY_FILE.exists():
                HISTORY_FILE.unlink()
            if PREFERENCES_FILE.exists():
                PREFERENCES_FILE.unlink()
            if MEMORY_FILE.exists():
                MEMORY_FILE.unlink()
            
            # Reset in-memory data
            self.conversation_history = []
            self.user_preferences = {}
            self.context_memory = {}
            
            return "All stored data has been cleared successfully."
        except Exception as e:
            return f"Error clearing data: {e}"
    
    def get_user_stats(self):
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
    
    def learn_from_interaction(self, user_input, response, sentiment, nlp_processor):
        # Store conversation history
        self.conversation_history.append({
            'timestamp': datetime.datetime.now(),
            'user_input': user_input,
            'response': response,
            'sentiment': sentiment
        })
        
        # Keep only last 100 interactions in memory (but save all to file)
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        # Extract user preferences
        tokens = nlp_processor.preprocess_text(user_input)
        for token in tokens:
            if token in self.user_preferences:
                self.user_preferences[token] += 1
            else:
                self.user_preferences[token] = 1
        
        # Save to persistent storage
        self.save_conversation_history()
        self.save_user_preferences()
        self.save_context_memory()