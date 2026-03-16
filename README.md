# AEGIS: Autonomous Ecosystem for General Intelligence & Systems 🚀

AEGIS is a proactive, agentic desktop AI assistant built for the #GeminiLiveAgentChallenge. Unlike standard voice assistants that only answer questions, AEGIS uses the **Gemini 2.5 Flash API** and Function Calling to actively control the PC, create files, install software, and monitor system health.

## 🛠️ Built With
* **Python & PyQt5:** Core logic and asynchronous Cybernetic UI.
* **Google Gemini API (2.5 Flash):** The Agentic Brain using Function Calling.
* **Semantic Router (SentenceTransformers):** Local intent routing to save API latency.
* **OpenCV & Biometrics:** Local facial recognition for secure system boot.
* **OS Libraries:** `psutil` (Proactive monitoring), `subprocess` (App execution), `pywhatkit` (Media).

## 🧪 How to Test AEGIS Locally (Reproducible Testing)

1. **Clone this repository:**
   `git clone https://github.com/YashAI060/AEGIS-Agentic-AI.git`
2. **Install the required dependencies:**
   `pip install google-genai SpeechRecognition pyqt5 psutil pywhatkit sentence-transformers opencv-python numpy`
3. **Set your API Key:**
   Open `main.py` and replace `"YOUR_GEMINI_API_KEY"` with your actual Google Gemini API Key.
4. **Train the Biometric Face Unlock (CRITICAL STEP):**
   Before starting AEGIS, the system needs to recognize you as the authorized user.
   * First, run `python generate_dataset.py` (Look into your webcam until it captures enough samples of your face).
   * Next, run `python train_model.py` (This will train the local security model on your face).
5. **Run the Application:**
   Double click the `Start_AEGIS.bat` file OR run `python interface.py` in your terminal. The camera will pop up to verify your identity before booting the main AI!
6. **Testing Commands:**
   * *Wake the system:* Say "Aegis"
   * *Agentic Task:* Say "Aegis, create a python file named hello.py with a print hello world statement and open it in VS Code."
   * *Local Reflex:* Say "Aegis, increase the volume."

## 📴 Offline Privacy Mode
AEGIS also includes a completely offline version that runs without any cloud APIs. To test the offline, privacy-first mode, run:
`python main_offline.py`

## ☁️ Proof of Google Cloud Integration
The core Agentic Brain is powered by the Google GenAI SDK. See the implementation in `main.py` where the `generate_content` method utilizes the `tools` parameter for function calling.
