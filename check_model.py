from google import genai
import os

# --- PASTE API KEY HERE ---
GENAI_API_KEY = "YOUR_API_KEY_HERE"

try:
    client = genai.Client(api_key=GENAI_API_KEY)
    print("Connecting to Google Servers...\n")
    
    # Available models list karein
    print("--- AVAILABLE MODELS FOR YOU ---")
    # 'v1beta' version mein models check kar rahe hain
    for model in client.models.list(config={"query_base": True}): 
        # Sirf generateContent wale models dikhayein (Chat wale)
        if "generateContent" in model.supported_actions:
            print(f"- {model.name}")
            
except Exception as e:
    print(f"Error: {e}")