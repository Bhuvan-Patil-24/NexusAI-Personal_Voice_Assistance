import speech_recognition as sr
import win32com.client
import webbrowser
import datetime
import os


speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    speaker.Speak(text)

def takeCommand():
    r = sr.Recognizer() #Recognizer class
    with sr.Microphone() as source: #Microphone class for input voice
        print("Listening...")
        r.pause_threshold = 1 #pause for 1 sec
        audio = r.listen(source) #listen to the audio from the microphone
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"Your Query: {query}\n")
        return query
    except Exception as e:
        print("Say that again please...")
        return "None"

if __name__ == "__main__":
    print("------< Welcome to Nexus AI >------")
    introtxt = "Hello! I am Nexus A.I. How can I help you today?"
    speak(introtxt)
    sites = {
        "google": "https://google.com",
        "youtube": "https://youtube.com",
        "wikipedia": "https://wikipedia.com",
    }
    apps = {
        "chrome": "C:\\Users\\Public\\Desktop\\Google Chrome.lnk",
        "canva": "C:\\Users\\patil\\OneDrive\\Desktop\\Canva.lnk",
        "notepad": "C:\\Windows\\System32\\notepad.exe",
        "calculator": "C:\\Windows\\System32\\calc.exe",
    }
    while True:
        
        query = takeCommand().lower()
        
        for site in sites:
            if site in query:
                speak(f"Opening {site}...")
                webbrowser.open(sites[site])
                break
        
        for app in apps:
            if app in query:
                speak(f"Opening {app}...")
                os.system(apps[app])
                break
        
        if 'goodbye' in query.strip():
            speak("Goodbye! Have a nice day!")
            break
        elif 'none' in query:
            continue
        elif 'the time' in query:
            curTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(curTime)
            speak(f"Sir, The time is {curTime}")
        elif 'play music' in query:
            # musicPath = "C:\\Users\\hp\\Music\\Faded.mp3"
            # speak("Playing music...")
            # os.system(f"open {musicPath}")
            speak("Playing music in YouTube...")
            # webbrowser.open("https://www.youtube.com/watch?v=yszisrGQsmY") #customising later on