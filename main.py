import speech_recognition as sr
import screen_brightness_control as sbc
import pyttsx3
import os
import sys
import time
import datetime
import pywhatkit
import pyautogui
from google import genai
from google.genai import types
from agent_tools import AEGIS_TOOLS, create_text_file, open_website, search_google, play_youtube_video, install_software, create_and_open_file

try:
    from orchestrator import AegisOrchestrator
    import aegis_offline as offline_brain
    from proactive import SystemMonitor
except ImportError as e:
    print(f"CRITICAL ERROR: Missing File. {e}")
    print("Ensure orchestrator.py, router_schema.py, and aegis_offline.py are in the same folder.")
    sys.exit()

GENAI_API_KEY = "YOUR_API_KEY_HERE"
ELEVENLABS_API_KEY = "YOUR_API_KEY_HERE"
WEATHER_API_KEY = "YOUR_API_KEY_HERE"
VOICE_ID = "pNInz6obpgDQGcFmaJgB" 

CONTACTS = { "mom": "+923001234567" }

# --- AEGIS STATE ---
IS_BUSY = False

def check_busy():
    return IS_BUSY

def ask_gemini(query):
    """The Intelligent Agentic Brain (Cloud LLM)"""
    if "PASTE" in GENAI_API_KEY: return "Please set your Gemini API Key."
    try:
        client = genai.Client(api_key=GENAI_API_KEY)
        sys_instr = (
            "You are AEGIS, an advanced AI assistant. "
            "You have access to tools to control the PC. Use them if the user asks you to do a task like creating a file or opening a site. "
            "If no tool is needed, just reply normally in Hinglish or English. Keep verbal answers concise."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=sys_instr,
                tools=AEGIS_TOOLS, # 👈 Giving AEGIS its capabilities!
                temperature=0.3,
            )
        )

        # IF GEMINI DECIDES TO USE A TOOL:
        if response.function_calls:
            for function_call in response.function_calls:
                print(f"\n[AGENT DECISION] Using Tool: {function_call.name}")
                
                args = function_call.args
                
                # Execute the corresponding function based on Gemini's choice
                if function_call.name == "create_text_file":
                    result = create_text_file(args['filename'], args['content'])
                    return f"Done Sir. I have created the file {args['filename']}."
                    
                elif function_call.name == "open_website":
                    result = open_website(args['url'])
                    return f"Opening the website for you, Sir."
                    
                elif function_call.name == "search_google":
                    result = search_google(args['query'])
                    return f"Searching the web for {args['query']}."

                # 👇 NEW YOUTUBE TOOL ADDED HERE
                elif function_call.name == "play_youtube_video":
                    result = play_youtube_video(args['search_query'])
                    return f"Playing it on YouTube for you."
                    
                # 👇 NEW TOOLS WILL BE ADDED HERE
                elif function_call.name == "install_software":
                    result = install_software(args['app_name'])
                    return f"Initiating the installation for {args['app_name']}, Sir."
                    
                elif function_call.name == "create_and_open_file":
                    result = create_and_open_file(args['filename'], args['content'], args['app_name'])
                    return f"File created and opened in {args['app_name']}, Sir."

        # FOR NORMAL CONVERSATION (No tool needed):
        return response.text.replace("*", "")

    except Exception as e: 
        print(f"Cloud Error Log: {e}")
        return "Sir, I encountered a cloud processing error."

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\rListening...", end="", flush=True)
        try: 
            # 👇 CORE CHANGES HERE 👇
            r.pause_threshold = 1.5        # Originally 0.5. Now waits for 1.5s of silence before stopping recording.
            r.non_speaking_duration = 0.5  # To ignore background noise and short breaths.
            
            # timeout=5 (Waits up to 5 seconds for the first sound)
            # phrase_time_limit=15 (Maximum length of a single sentence is 15 seconds)
            audio = r.listen(source, timeout=5, phrase_time_limit=15) 
            
        except Exception as e: 
            return "None"
            
    try:
        print("\rProcessing...", end="", flush=True)
        query = r.recognize_google(audio, language='en-in')
        print(f"\nUser: {query}")
        return query.lower()
    except Exception as e: 
        return "None"

def wait_for_wake_word():
    """Silently waits for the Wake Word in the background"""
    r = sr.Recognizer()
    with sr.Microphone(device_index=3) as source:
        print("\n[SLEEP MODE] Waiting for wake word ('Aegis')...", end="", flush=True)
        
        # Moved calibration outside the loop to prevent mic freeze
        r.pause_threshold = 0.5
        r.adjust_for_ambient_noise(source, duration=1) 
        
        while True:
            try:
                audio = r.listen(source, timeout=1, phrase_time_limit=3)
                word = r.recognize_google(audio, language='en-in').lower()
                
                # Return TRUE if wake word is detected (No break)
                if "aegis" in word or "ages" in word or "hey jesus" in word or "eggis" in word or "wake up" in word:
                    return True 
            except Exception:
                # If nothing is heard, continue looping silently
                pass

def speak_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"Sir, the time is {current_time}")

def execute_volume(query):
    if "up" in query or "increase" in query or "badhao" in query: 
        pyautogui.press("volumeup"); speak("Volume increased.")
    elif "down" in query or "decrease" in query or "kam" in query: 
        pyautogui.press("volumedown"); speak("Volume decreased.")
    elif "unmute" in query: 
        pyautogui.press("volumemute"); speak("Unmuted.")
    elif "mute" in query: 
        pyautogui.press("volumemute"); speak("Muted.")

def execute_brightness(query):
    try:
        current = sbc.get_brightness(display=0)[0]
        if "up" in query or "badhao" in query or "increase" in query:
            sbc.set_brightness(min(current + 20, 100))
            speak("Brightness increased.")
        elif "down" in query or "kam" in query or "decrease" in query:
            sbc.set_brightness(max(current - 20, 0))
            speak("Brightness decreased.")
    except Exception as e:
        print(f"Brightness Error: {e}")
        speak("Brightness control supported nahi hai.")

def execute_window_control(query):
    if "minimize" in query:
        pyautogui.hotkey('win', 'down')
        speak("Window minimized.")
    elif "close" in query:
        pyautogui.hotkey('alt', 'f4')
        speak("Window closed.")
    elif "switch" in query:
        pyautogui.hotkey('alt', 'tab')
        speak("Switching window.")
    elif "show desktop" in query or "hide" in query:
        pyautogui.hotkey('win', 'd')
        speak("Desktop shown.")

def execute_media_control(query):
    # Treats 'post' as 'pause'
    if "pause" in query or "resume" in query or "stop" in query or "post" in query:
        pyautogui.press('playpause')
        speak("Media toggled.")
    elif "next" in query or "change" in query:
        pyautogui.press('nexttrack')
        speak("Playing next track.")
    # Treats 'first' as 'previous'
    elif "previous" in query or "first" in query:
        pyautogui.press('prevtrack')
        speak("Playing previous track.")

def execute_pc_state(query):
    if "lock" in query:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        speak("PC Locked.")
    elif "sleep" in query:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        speak("Putting PC to sleep.")

# --- OFFLINE VOICE SETUP ---
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)

def speak(text):
    """Speaks instantly using Offline Windows Voice"""
    print(f"AEGIS: {text}") 
    engine.say(text)
    engine.runAndWait()

def main_loop():
    global IS_BUSY
    aegis = AegisOrchestrator()
    
    # Start Proactive Monitor (Previous feature)
    try:
        from proactive import SystemMonitor
        monitor = SystemMonitor(speak, check_busy)
        monitor.start()
    except Exception as e:
        print(f"[INFO] Proactive Monitor error: {e}")

    speak("AEGIS Online. Sleep mode active.")

    while True:
        # --- OUTER LOOP: WAITING FOR WAKE WORD ---
        IS_BUSY = False 
        if wait_for_wake_word():
            speak("Yes sir? I am online.")
            
            # --- INNER LOOP: CONTINUOUS LISTENING MODE ---
            while True:
                IS_BUSY = False # Proactive system can operate while listening
                query = take_command() 
                
                # If nothing is heard, loop back and listen again (silently)
                if query == "None": 
                    continue 

                IS_BUSY = True # Command received, starting processing!

                # 1. STANDBY CHECK (Put Aegis to sleep)
                if "go to sleep" in query or "standby" in query or "stop listening" in query:
                    speak("Going back to standby mode. Wake me up if you need me.")
                    break # Break inner loop, AEGIS returns to waiting for Wake Word

                # 2. ROUTER DECISION
                decision = aegis.route_query(query)
                print(f"[ROUTER]: Intent={decision.intent} | Route={decision.route}")

                if decision.clarification_needed:
                    speak("I'm not sure. Did you mean to search or save?")
                    continue

                if decision.privacy_risk and decision.route == "CLOUD_LLM":
                    speak("Sensitive info detected. Switching to offline mode.")
                    decision.route = "LOCAL_LLM"

                # 3. EXECUTION
                if decision.route == "REFLEX":
                    if decision.intent == "SYSTEM_CONTROL":
                        # Volume Check
                        if "volume" in query or "mute" in query or "unmute" in query: 
                            execute_volume(query)
                        # Standalone UP/DOWN/INCREASE/DECREASE Check
                        elif query.strip() in ["down", "decrease", "kam karo"]: 
                            pyautogui.press("volumedown"); speak("Volume decreased.")
                        elif query.strip() in ["up", "increase", "badhao"]: 
                            pyautogui.press("volumeup"); speak("Volume increased.")
                        # Brightness Check
                        elif "brightness" in query: 
                            execute_brightness(query)
                        
                        # --- APPS CHECK (More flexible) ---
                        elif "youtube" in query and "open" in query: 
                            import webbrowser
                            webbrowser.open("https://www.youtube.com")
                            speak("Opening YouTube.")
                        elif "spotify" in query: # NEW SPOTIFY LOGIC
                            os.system("start spotify")
                            speak("Opening Spotify.")
                        elif "chrome" in query: 
                            os.system("start chrome"); speak("Opening Chrome.")
                        elif "vs code" in query or "code" in query: 
                            os.system("start code"); speak("Opening VS Code.") # Fixed ICU Error
                        elif "notepad" in query: 
                            os.system("start notepad"); speak("Opening Notepad.")
                        elif "settings" in query: 
                            os.system("start ms-settings:"); speak("Opening Settings.")
                        elif "task manager" in query: 
                            pyautogui.hotkey('ctrl', 'shift', 'esc'); speak("Task Manager opened.")
                        elif "explorer" in query: 
                            os.system("explorer"); speak("Explorer opened.")
                        
                        # Shutdown PC Check
                        elif "shutdown" in query or "exit" in query or "stop" in query: 
                            speak("Shutting down core systems. Goodbye.")
                            sys.exit()
                    
                    elif decision.intent == "WINDOW_CONTROL":
                        try: execute_window_control(query)
                        except: pass
                    elif decision.intent == "MEDIA_CONTROL":
                        try: execute_media_control(query)
                        except: pass
                    elif decision.intent == "PC_STATE":
                        try: execute_pc_state(query)
                        except: pass
                    elif decision.intent == "TIME_CHECK":
                        speak_time()
                    elif decision.intent == "AEGIS_STANDBY":
                        speak("Going back to standby mode.")
                        break # Put back to sleep

                elif decision.route == "LOCAL_LLM":
                    try:
                        response = offline_brain.ask_ai(query)
                        speak(response)
                    except Exception as e:
                        print(f"Offline Brain Local Error: {e}")

                elif decision.route == "CLOUD_LLM":
                    response = ask_gemini(query)
                    speak(response)

                elif decision.route == "TOOL_CHAIN":
                    print(f"[DEBUG] Executing Tools: {decision.tools}") 
                    if "google_search" in decision.tools:
                        speak("Searching Google...")
                        pywhatkit.search(query)
                    elif "youtube_play" in decision.tools:
                        # Remove extra words so only the video name remains
                        song = query.replace("play", "").replace("chalao", "").replace("on youtube", "").replace("video", "").strip()
                        
                        if song == "": # If the user only said "play"
                            pyautogui.press("playpause")
                            speak("Resuming media.")
                        else:
                            speak(f"Playing {song} on YouTube.")
                            try: 
                                pywhatkit.playonyt(song)
                            except: 
                                # Fallback: Force Chrome from OS level
                                os.system(f'start chrome "https://www.youtube.com/results?search_query={song}"')
                    elif "whatsapp_api" in decision.tools:
                        speak("WhatsApp protocol initiating...")

if __name__ == "__main__":
    main_loop()