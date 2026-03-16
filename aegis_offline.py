import speech_recognition as sr
import os
import sys
import time
import datetime
import pywhatkit
import pyautogui
import ollama
import pyttsx3 
import json # <--- NEW OFFLINE VOICE LIBRARY

# --- CONFIGURATION ---
# No API Key needed anymore (Only for Weather if you want to keep that feature)
WEATHER_API_KEY = "PASTE_WEATHER_API_KEY_HERE"
MEMORY_FILE = "aegis_memory.json"

CONTACTS = { "mom": "+923001234567" } 

# --- OFFLINE VOICE SETUP ---
engine = pyttsx3.init('sapi5') # Windows Audio Engine
voices = engine.getProperty('voices')

# Index 0 = Male (David), Index 1 = Female (Zira)
# You can change the voice by changing 0 or 1 here
engine.setProperty('voice', voices[0].id) 
engine.setProperty('rate', 170) # Speed (Low = Deep, High = Fast)

def speak(text):
    print(f"AEGIS: {text}")
    engine.say(text)
    engine.runAndWait() # This will hold the code while speaking

def load_memory():
    """Loads old data from file (with Error Handling)"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If file is empty or corrupt, return empty dictionary
            return {}
    return {} # If file doesn't exist, return empty dictionary

def save_memory(key, value):
    """Saves new data to file"""
    data = load_memory()
    data[key] = value
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    return True

# --- NEW: SMART MEMORY EXTRACTION ---
def extract_and_save(text):
    """Asks Llama what to save"""
    try:
        # Tell Llama to extract data in JSON format
        sys_prompt = (
            "Extract the information to remember from the user's sentence. "
            "Output ONLY a JSON object with a 'key' (short noun) and a 'value' (fact). "
            "Example Input: 'Remember my bike color is red' -> Output: {\"key\": \"bike_color\", \"value\": \"red\"} "
            "Example Input: 'Remember the key is in the drawer' -> Output: {\"key\": \"key_location\", \"value\": \"drawer me\"} "
            "Do NOT write any extra text, just the JSON."
        )
        
        response = ollama.chat(model='llama3.1:latest', messages=[
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': text},
        ])
        
        # Llama's response will be a string, convert it to a Dictionary
        result = response['message']['content']
        # Sometimes Llama adds extra text, so cleanup is necessary
        start = result.find('{')
        end = result.find('}') + 1
        clean_json = result[start:end]
        
        data = json.loads(clean_json)
        key = data['key']
        value = data['value']
        
        save_memory(key, value)
        return key, value
    except Exception as e:
        print(f"Memory Error: {e}")
        return None, None

def get_memory(key):
    """Retrieves a specific item"""
    data = load_memory()
    return data.get(key, None)

# --- WEATHER FUNCTION (Optional - Needs Internet) ---
import requests # Request still needed for Weather
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        if res["cod"] != "404":
            return f"{res['main']['temp']} degrees celsius"
        return "City not found."
    except: return "Connection Error."

# --- OFFLINE AI BRAIN (LLAMA 3.1) ---
def ask_ai(query):
    try:
        # Load all memories
        memories = load_memory()
        # Convert memories to text so the Brain can read them
        memory_text = ", ".join([f"{k}: {v}" for k, v in memories.items()])
        
        sys_instruction = (
            f"You are AEGIS. "
            f"Context/Memories: [{memory_text}]. "
            "Use these memories to answer if relevant. "
            "Reply in Hinglish. Keep answers short."
        )

        response = ollama.chat(model='llama3.1:latest', messages=[
            {'role': 'system', 'content': sys_instruction},
            {'role': 'user', 'content': query},
        ])
        return response['message']['content']
    except: return "Brain offline."

# --- MAIN LOGIC ---
def take_command():
    r = sr.Recognizer()
    with sr.Microphone(device_index=3) as source:  # <-- Incorrect (Static)
        print("\rListening...", end="", flush=True)
        try: 
            r.pause_threshold = 1.0
            # Adjust ambient noise to hear even in noisy environments
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except: return "None"
    try:
        print("\rProcessing...", end="", flush=True)
        # Note: 'recognize_google' still uses internet (text-to-speech is offline)
        query = r.recognize_google(audio, language='en-in')
        print(f"\nUser: {query}")
    except: return "None"
    return query.lower()

if __name__ == "__main__":
    # Face Unlock Import Check
    verified = True
    try:
        import face_unlock
        speak("Biometric Scan Initiated.")
        if not face_unlock.recognize_user(): 
            speak("Access Denied.")
            verified = False
    except ImportError:
        pass

    if verified:
        name = get_memory("name")
        if name:
            speak(f"Welcome back, {name}. Systems Online.")
        else: 
            speak("AEGIS Systems Online.")
        while True:
            query = take_command()
            if query == "None": continue

            if 'stop' in query or 'exit' in query:
                speak("Shutting down.")
                break 

            elif 'remember' in query or 'yaad rakhna' in query or 'yaad rakho' in query:
                speak("Memorizing...")
                key, value = extract_and_save(query)
                if key:
                    speak(f"Okay, saved that {key} is {value}.")
                else:
                    speak("Sorry, I couldn't understand what to save.")
            
            elif 'weather' in query:
                speak("Checking sensors...")
                report = get_weather("Karachi")
                speak(f"Current temperature is {report}")

            elif 'time' in query:
                strTime = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {strTime}")

            elif 'play' in query:
                song = query.replace('play', 'chla')
                speak(f"Playing {song}")
                pywhatkit.playonyt(song)

            elif 'volume up' in query:
                pyautogui.press("volumeup")
                speak("Volume Increased.")

            elif 'volume down' in query:
                pyautogui.press("volumedown")
                speak("Volume Decreased.")
            
            else:
                # ASK LLAMA BRAIN
                response = ask_ai(query)
                speak(response)