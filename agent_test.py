from google import genai
from google.genai import types
import os

# --- 1. APNA TOOL BANAO (Skill) ---
def create_text_file(filename: str, content: str) -> str:
    """Creates a new text file on the computer with the given content."""
    try:
        with open(filename, "w") as f:
            f.write(content)
        print(f"[ACTION TAKEN] File '{filename}' created!")
        return f"Success: File {filename} has been created."
    except Exception as e:
        return f"Error creating file: {e}"

# --- 2. GEMINI KO TOOL SIKHAO ---
API_KEY = "YOUR_GEMINI_API_KEY" # Apni API key dalein
client = genai.Client(api_key=API_KEY)

def chat_with_agent(user_message):
    print(f"\nUser: {user_message}")
    
    # Yahan hum Gemini ko apni skills bata rahe hain
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_message,
        config=types.GenerateContentConfig(
            tools=[create_text_file], # 👈 Yeh sabse important line hai!
            temperature=0.0,
        )
    )

    # Gemini ka decision check karna
    if response.function_calls:
        for function_call in response.function_calls:
            print(f"[GEMINI THINKING] Gemini decided to use tool: {function_call.name}")
            
            # Gemini ne jo parameters soche hain, unhe extract karna
            if function_call.name == "create_text_file":
                args = function_call.args
                # Tool ko actually execute karna
                result = create_text_file(filename=args['filename'], content=args['content'])
                print(f"AEGIS: I have created the file for you.")
    else:
        # Agar koi tool use nahi karna, toh normal reply
        print(f"AEGIS: {response.text}")

# --- 3. TEST KAREIN ---
if __name__ == "__main__":
    # Test 1: Normal baatchit
    chat_with_agent("Hi, tum kaun ho?")
    
    # Test 2: Agentic Task (File creation)
    chat_with_agent("Bhai ek kaam kar, 'shopping_list.txt' naam ki file bana aur usme likh de: 1. Doodh 2. Ande")