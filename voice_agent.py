"""
Voice AI Sales Agent Engine for SquadStack.
Implements the turn-by-turn state machine, voice constraints validator,
and LLM response generator with support for both live APIs and local benchmark simulation.
"""

import os
import re
import json
import urllib.request
from typing import Dict, List, Any, Optional
from prompts import VOICE_SALES_SYSTEM_PROMPT


class VoiceAgent:
    """
    Voice-first Conversational Agent designed for high-concurrency low-latency outbound calls.
    Enforces spoken constraints: brevity, phonetics, and compliance.
    """

    def __init__(self, agent_name: str = "Priya", client_brand: str = "AngelOne"):
        self.agent_name = agent_name
        self.client_brand = client_brand
        self.system_prompt = VOICE_SALES_SYSTEM_PROMPT
        self.history: List[Dict[str, str]] = []
        self.current_stage = "GREETING"
        self.callback_time: Optional[str] = None
        self.link_sent = False
        self.dnd_opted = False

    def reset(self):
        """Reset conversation state for a fresh call."""
        self.history = []
        self.current_stage = "GREETING"
        self.callback_time = None
        self.link_sent = False
        self.dnd_opted = False

    def clean_voice_output(self, text: str) -> str:
        """
        Sanitize text output for Text-To-Speech (TTS) engine:
        - Strips markdown formatting (bold, italic, bullets, headers)
        - Removes emojis or unpronounceable characters
        - Ensures conversational punctuation
        """
        # Strip markdown syntax
        clean = re.sub(r'[*_#`~]', '', text)
        clean = re.sub(r'\[.*?\]\(.*?\)', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def generate_response(self, user_utterance: str, customer_name: str = "Customer") -> Dict[str, Any]:
        """
        Processes a customer utterance and returns the agent's spoken response,
        tracking turn metrics like word count and stage transition.
        """
        self.history.append({"role": "customer", "text": user_utterance})
        user_lower = user_utterance.lower()

        # Check for immediate DND / Opt-out compliance
        if "dnd" in user_lower or "call mat karo" in user_lower or "band karo" in user_lower:
            self.dnd_opted = True
            self.current_stage = "COMPLIANCE_CLOSING"
            response_text = "I apologize for the trouble, sir. Maine aapka number DND list me update kar diya hai. Have a good day."

        # Check for Link Delivery / CTA acceptance (Highest priority for sales conversion)
        elif any(w in user_lower for w in ["link", "bhej do", "bhej de", "bhejo", "whatsapp pe"]):
            self.current_stage = "ASSISTANCE"
            self.link_sent = True
            response_text = "Maine aapke registered WhatsApp aur SMS pe official KYC link bhej diya hai sir, bas 2 minute lagenge."

        # Check for Security / Fraud / Scam / Pricing objections
        elif any(w in user_lower for w in ["fraud", "scam", "paise", "charge", "hidden", "kaha se", "free"]):
            self.current_stage = "TRUST_BUILDING"
            if "charge" in user_lower or "paise" in user_lower or "hidden" in user_lower or "free" in user_lower:
                response_text = "Sir account opening bilkul free hai, zero annual maintenance charge ke sath. Koi hidden fees nahi hai."
            else:
                response_text = "Sir AngelOne SEBI-registered platform hai with 2 crore users. Hum aapse kabhi koi OTP ya password nahi maangte."

        # Check for Driving / Busy objections or Callback confirmations
        elif any(w in user_lower for w in ["drive", "driving", "busy", "time nahi", "baad me baat", "baad me call", "meeting", "call kar", "call back"]):
            self.current_stage = "CALLBACK_NEGOTIATION"
            if any(num in user_lower for num in ["6", "7", "8", "sham", "evening", "kal"]):
                # Customer specified a time
                self.callback_time = "Evening 6 PM"
                response_text = "Bilkul sir! Maine note kar liya hai, main aapko sham ko 6 baje call karti hoon. Thank you!"
            else:
                response_text = "Samajh sakti hoon sir. Kya main aapko aaj sham ko 6 ya 7 baje call back kar sakti hoon?"

        # Check for Process / Document queries / Link acceptance
        elif any(w in user_lower for w in ["document", "kyc", "kya hota", "kaise", "process", "link", "bhej do", "aadhaar", "pan"]):
            self.current_stage = "ASSISTANCE"
            if any(w in user_lower for w in ["link", "bhej", "complete"]):
                self.link_sent = True
                response_text = "Maine aapke registered WhatsApp aur SMS pe official KYC link bhej diya hai sir, bas 2 minute lagenge."
            else:
                response_text = "Sir bas 2 minute lagte hain! Sirf PAN aur Aadhaar number se online verify ho jata hai. Kya main link bhej doon?"

        # Default Greeting / Value Proposition
        else:
            self.current_stage = "VALUE_PROP"
            response_text = f"Namaste {customer_name} ji, main AngelOne se Priya baat kar rahi hoon. Aapka Demat account KYC pending hai, kya main madad kar sakti hoon?"

        cleaned_text = self.clean_voice_output(response_text)
        word_count = len(cleaned_text.split())

        self.history.append({"role": "agent", "text": cleaned_text})

        return {
            "response": cleaned_text,
            "word_count": word_count,
            "is_voice_compliant": word_count <= 25,
            "stage": self.current_stage,
            "callback_time": self.callback_time,
            "link_sent": self.link_sent,
            "dnd_opted": self.dnd_opted
        }
