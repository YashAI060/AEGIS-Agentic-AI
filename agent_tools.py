# agent_tools.py
import os
import webbrowser
import pywhatkit
import subprocess

def create_text_file(filename: str, content: str) -> str:
    """Creates a new text file on the computer with the given content."""
    try:
        # Default save to desktop so it's easy to find (optional)
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"[TOOL EXECUTED] Created file: {filepath}")
        return f"File '{filename}' successfully created on the Desktop."
    except Exception as e:
        return f"Failed to create file: {e}"

def open_website(url: str) -> str:
    """Opens a specific website URL in the default web browser."""
    try:
        # Ensure url has http
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        print(f"[TOOL EXECUTED] Opened website: {url}")
        return f"Successfully opened {url} in the browser."
    except Exception as e:
        return f"Failed to open website: {e}"

def search_google(query: str) -> str:
    """Searches for a query on Google in the web browser."""
    try:
        pywhatkit.search(query)
        print(f"[TOOL EXECUTED] Searched Google for: {query}")
        return f"Successfully searched Google for '{query}'."
    except Exception as e:
        return f"Failed to search Google: {e}"

def play_youtube_video(search_query: str) -> str:
    """Plays a specific video, song, movie, or show directly on YouTube."""
    try:
        pywhatkit.playonyt(search_query)
        print(f"[TOOL EXECUTED] Playing on YouTube: {search_query}")
        return f"Successfully playing {search_query} on YouTube."
    except Exception as e:
        return f"Failed to play on YouTube: {e}"

def install_software(app_name: str) -> str:
    """Installs a software or application on the Windows PC using winget."""
    try:
        print(f"[TOOL EXECUTED] Initiating installation for: {app_name}...")
        # We will open a new CMD window so you can see the installation progress
        command = f"winget install {app_name} --accept-package-agreements --accept-source-agreements"
        os.system(f'start cmd /k "{command}"') 
        return f"Started the installation process for {app_name}. A terminal window has opened to show the progress."
    except Exception as e:
        return f"Failed to install software: {e}"

def create_and_open_file(filename: str, content: str, app_name: str) -> str:
    """Creates a file with content and immediately opens it in a specific application."""
    try:
        # Save the file to Desktop
        filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"[TOOL EXECUTED] Created file: {filepath}")
        
        # New and safe logic to open app (Subprocess)
        app_cmd = app_name.lower()
        
        if "vs code" in app_cmd or "code" in app_cmd:
            # shell=True prevents VS Code from crashing
            subprocess.Popen(["code", filepath], shell=True) 
        elif "notepad" in app_cmd:
            subprocess.Popen(["notepad.exe", filepath], shell=True)
        else:
            # If it's any other app, use the default Windows opener
            os.startfile(filepath)
            
        return f"Successfully created '{filename}' and opened it in {app_name}."
    except Exception as e:
        return f"Created the file, but failed to open it: {e}"

# 🔥 UPDATE THIS LIST AT THE BOTTOM OF THE FILE
AEGIS_TOOLS = [create_text_file, open_website, search_google, play_youtube_video, install_software, create_and_open_file]