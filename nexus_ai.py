import time
from threading import Thread
from config import WAKE_WORD
from nlp_processor import NLPProcessor
from data_manager import DataManager
from audio_handler import AudioHandler
from command_processor import CommandProcessor
# import traceback

class NexusAI:
    def __init__(self):
        print("Initializing NexusAI components...")
        
        # Initialize core components
        self.data_manager = DataManager()
        self.nlp_processor = NLPProcessor()
        self.audio_handler = AudioHandler()
        self.command_processor = CommandProcessor(
            self.nlp_processor, 
            self.data_manager
        )
        
        # Assistant state
        self.is_listening = False
        self.wake_word = WAKE_WORD.lower()
        self.running = True
        
        print("NexusAI initialization complete!")
        
        # Greet user on startup
        self.audio_handler.speak("Hello! I'm NexusAI, your personal voice assistant. Say 'Nexus' followed by your command to wake me up.")
    
    def handle_wake_detection(self, audio_input):
        if self.wake_word in audio_input or self.is_listening:
            # Process the command
            response, should_exit = self.command_processor.process_command(audio_input)
            self.audio_handler.speak(response)
            
            if should_exit:
                self.running = False
                return
            
            # Set listening state for follow-up commands
            self.is_listening = True
            
            # Reset listening state after a delay
            def reset_listening():
                time.sleep(10)
                self.is_listening = False
            
            Thread(target=reset_listening, daemon=True).start()
    
    def run(self):
        while self.running:
            try:
                # Listen for input
                audio_input = self.audio_handler.listen()
                
                if audio_input:
                    self.handle_wake_detection(audio_input)
                
            except KeyboardInterrupt:
                print("\nShutting down NexusAI...")
                self.shutdown()
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                # traceback.print_exc()
                self.audio_handler.speak("Sorry, I encountered an error. Please try again.")
    
    def shutdown(self):
        self.running = False
        
        # Save all data before shutdown
        try:
            self.data_manager.save_all_data()
            print("Data saved to DB.")
        except Exception as e:
            print(f"Error saving data: {e}")
        
        self.audio_handler.speak("Goodbye Sir! Have a great day!")
        print("NexusAI shutdown complete.")
    
    def get_system_info(self):
        info = {
            'is_listening': self.is_listening,
            'wake_word': self.wake_word,
            'running': self.running,
            'data_info': self.data_manager.get_storage_info() if hasattr(self.data_manager, 'get_storage_info') else None
        }
        return info

def main():
    try:
        print("=" * 50)
        print("🤖 NexusAI - Advanced Voice Assistant")
        print("=" * 50)
        print()
        # Create and run the assistant
        assistant = NexusAI()
        
        try:
            assistant.run()
        except KeyboardInterrupt:
            assistant.shutdown()
            
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("\nPlease install missing packages:")
        print("pip install speechrecognition pyttsx3 wikipedia requests pyaudio nltk textblob spacy")
        print("python -m spacy download en_core_web_sm")
        
    except Exception as e:
        print(f"Failed to start NexusAI: {e}")

if __name__ == "__main__":
    main()