import re
import numpy as np
from sentence_transformers import SentenceTransformer, util
from router_schema import RouterDecision

class AegisOrchestrator:
    def __init__(self):
        print(">> Loading Semantic Router... (First time may take a minute)")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.sensitive_keywords = ["password", "bank", "card", "otp", "secret", "medical", "address"]
        
        # --- 1. REFLEX PATTERNS (Fixed Spotify & Mic Mishearings) ---
        self.reflex_patterns = {
            "SYSTEM_CONTROL": [
                r"(shutdown|turn off|restart pc|reboot pc)\b",
                r"(volume up|volume down|mute|unmute|volume increase|increase volume|volume kam|volume badhao)\b",
                r"(brightness up|brightness down|brightness kam|brightness badhao|increase brightness|decrease brightness)\b", 
                r"^(up|down|increase|decrease|kam karo|badhao)$", 
                # 👇 Added "youtube on karo" and "youtube kholo"
                r"(open chrome|chrome open|open vs code|code open|open notepad|open settings|open task manager|open file explorer|open youtube|youtube on karo|youtube kholo|open spotify|spotify)\b" 
            ],
            "WINDOW_CONTROL": [
                r"(minimize|close window|switch window|show desktop|hide windows)\b"
            ],
            "MEDIA_CONTROL": [
                # Added "post" (for pause) and "first" (for previous)
                r"(pause|resume|next|previous|change|stop video|stop music|stop song|play next|post video|post|first video|first)\b" 
            ],
            "PC_STATE": [
                r"(lock pc|lock screen|sleep pc)\b"
            ],
            "AEGIS_STANDBY": [
                r"(go to sleep|standby|take a rest|stop listening|sleep mode|close aegis|exit aegis|stop aegis|just stop)\b" 
            ],
            "TIME_CHECK": [
                r"(what is the time|tell me the time|time please)\b"
            ]
        }

        # --- 2. SEMANTIC INTENTS ---
        self.intent_examples = {
            "WEB_SEARCH": [
                "who won the match", "weather in karachi", "latest news", "stock price", 
                "search on google", "search about", "find on google", "google par dhundo"
            ],
            # 🔥 ALL COMPLEX TASKS WILL NOW GO TO AGENTIC_TASK
            "AGENTIC_TASK": [  
                "ek file bnao", "create a text file", "make a file", "txt file bnao", 
                "netmeds.com kholo", "open mirror.com", "website open karo", "go to facebook.com", 
                "play tarak mehta ka ulta chashma", "youtube par chalao", "play arijit singh songs", "song chalao",
                # 👇 NEW EXAMPLES
                "vlc install karo", "install spotify", "app download karo", "install node js",
                "python file bana kar vs code mein kholo", "notepad mein ek note banao"
            ],
            "MEMORY_WRITE": ["remember that i like pizza", "save my name", "write this in memory", "yaad rakhna"], 
            "MEMORY_READ": ["who am i", "what is my name", "do you know my job", "mera naam kya hai"],
            "CREATIVE_CHAT": ["write a poem", "tell me a joke", "how are you", "hello", "hi", "bor ho raha hun"]
        }
        
        self.intent_embeddings = {
            k: self.model.encode(v) for k, v in self.intent_examples.items()
        }

    def _check_policy(self, query):
        if any(word in query.lower() for word in self.sensitive_keywords): return True
        return False

    def route_query(self, query) -> RouterDecision:
        query_lower = query.lower()

        # LAYER 1: REFLEX
        for intent, patterns in self.reflex_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return RouterDecision(intent=intent, route="REFLEX", confidence=1.0, privacy_risk=False, 
                                          tools=["os_control"] if intent == "SYSTEM_CONTROL" else ["time_tool"])

        # LAYER 2: POLICY
        is_sensitive = self._check_policy(query_lower)
        
        # LAYER 3: SEMANTIC
        query_emb = self.model.encode(query)
        scores = {}
        for intent, examples_emb in self.intent_embeddings.items():
            cos_scores = util.cos_sim(query_emb, examples_emb)[0]
            scores[intent] = float(cos_scores.max().item())

        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_score = sorted_intents[0]

        # Logic & Planning
        if top_score < 0.25:
            # Fallback: If local router fails, give it to Intelligent Gemini!
            return RouterDecision(intent="UNKNOWN", route="CLOUD_LLM", confidence=top_score, privacy_risk=is_sensitive, tools=[])

        decision = RouterDecision(intent=top_intent, route="LOCAL_LLM", confidence=top_score, privacy_risk=is_sensitive, tools=[])

        if top_intent == "WEB_SEARCH":
            decision.route = "LOCAL_LLM" if is_sensitive else "TOOL_CHAIN"
            decision.tools = ["google_search"]

        elif top_intent == "AGENTIC_TASK":  # 🔥 NEW ROUTE
            decision.route = "CLOUD_LLM"    # Will directly go to Gemini to clearly use tools!
            decision.tools = ["gemini_chat"]

        elif top_intent == "MEMORY_WRITE":
            decision.route = "LOCAL_LLM"
            decision.tools = ["extract_kv", "json_save"]

        elif top_intent == "CREATIVE_CHAT":
            decision.route = "LOCAL_LLM" if is_sensitive else "CLOUD_LLM"
            decision.tools = ["gemini_chat"]

        elif top_intent == "WHATSAPP":
             decision.route = "TOOL_CHAIN"
             decision.tools = ["whatsapp_api"]
             decision.requires_confirmation = True 
        
        return decision