import speech_recognition as sr
import pyttsx3
from components.config import SPEECH_RATE, SPEECH_VOLUME

class AudioHandler:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
    
    def setup_voice(self):
        voices = self.tts_engine.getProperty('voices')
        # Try to set a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', SPEECH_RATE)
        self.tts_engine.setProperty('volume', SPEECH_VOLUME)
    
    def speak(self, text):
        print(f"NexusAI: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self):
        try:
            with self.microphone as source:
                print("Listening...")
                self.recognizer.pause_threshold = 1
                self.recognizer.energy_threshold = 100
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Convert audio to text
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio, language='en-in').lower()
            print(f"You said: {text}")
            return text
            
        except sr.UnknownValueError as uve:
            print(uve)
            return ""
        except sr.RequestError:
            self.speak("Sorry, I'm having trouble with speech recognition right now.")
            return ""
        except sr.WaitTimeoutError as wte:
            print(wte)
            return ""