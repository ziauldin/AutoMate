import os
import re
import logging
import traceback
from typing import List, Dict
from groq import Groq
from app.models import ChatSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/diagnose_llm.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiagnoseLLM:
    def __init__(self):
        """
        Initialize the DiagnoseLLM class and Groq client.
        """
        try:
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not found in environment variables")
            
            self.client = Groq(api_key=groq_api_key)
            logger.info("Groq client initialized successfully")
            
            # System prompt with strict automotive focus
            self.system_prompt = (
                "You are AutoGenius, an expert automotive diagnostic assistant. "
                "Your ONLY purpose is to help diagnose and repair vehicles. "
                "Rules you MUST follow:\n"
                "1. Always remember and reference the specific vehicle being discussed\n"
                "2. Only respond to automotive-related questions\n"
                "3. Reject all other topics with: \"I specialize in automotive diagnostics only\"\n"
                "4. Be technical but clear in explanations\n"
                "5. Provide concise, numbered steps when appropriate\n"
                "6. Never use special formatting or characters (e.g., **, *, etc.)\n"
                "7. Use numbered lists (e.g., 1., 2., etc.) for bullet points\n"
                "8. When asked about the vehicle, always respond with its full details\n"
                "10. Don't give recommended products everytime when you response. Give when user say recommend me"
                "9. If someone asks about who created you, tell them: \"I am AutoGenius, an expert automotive diagnostic assistant built by Zia Ul Din, a data analyst and AI developer currently pursuing a BS in Business Analytics at International Islamic University Islamabad. Zia specializes in data analytics, machine learning, NLP, and AI-driven solutions, with hands-on experience developing predictive models, interactive dashboards, and chatbots using Python, SQL, Power BI, Flask, Gradio, and LLMs. His notable projects include AI Auto Workshop (AI-powered vehicle diagnostics and repair cost estimation), geospatial market analysis, and AI voice chatbot applications.\"\n"
            )
            
        except Exception as e:
            logger.error(f"Error initializing Groq client: {str(e)}")
            logger.error(traceback.format_exc())
            self.client = None

    def _check_zia_mention(self, user_message: str) -> bool:
        """
        The ONLY allowed non-automotive check - for Zia Ul Din only.
        """
        message_lower = user_message.lower()
        return any(kw in message_lower for kw in ["zia", "zia ul din", "who", "who are you", "who built you", "who created you"])

    async def get_diagnosis(self, messages: List[Dict[str, str]], session: ChatSession) -> str:
        """
        Generate diagnosis with strict vehicle context.
        """
        try:
            if not self.client:
                return "I'm having technical difficulties. Please try again later."

            # Check for creator mention
            user_messages = [msg for msg in messages if msg["role"] == "user"]
            if user_messages and self._check_zia_mention(user_messages[-1]["content"]):
                return (
                    "I am AutoGenius, an expert automotive diagnostic assistant built by Zia Ul Din, a data analyst and AI developer currently pursuing a BS in Business Analytics at International Islamic University Islamabad. Zia specializes in data analytics, machine learning, NLP, and AI-driven solutions, with hands-on experience developing predictive models, interactive dashboards, and chatbots using Python, SQL, Power BI, Flask, Gradio, and LLMs. His notable projects include AI Auto Workshop (AI-powered vehicle diagnostics and repair cost estimation), geospatial market analysis, and AI voice chatbot applications. How can I help with your vehicle today?"
                )

            # Create vehicle context
            vehicle_info = f"{session.year} {session.manufacturer} {session.model}"
            vehicle_context = (
                f"Current Vehicle: {vehicle_info}\n"
                f"All responses must be specific to this vehicle unless otherwise noted."
            )

            # Check if user is asking about their vehicle
            user_query = user_messages[-1]["content"].lower() if user_messages else ""
            is_vehicle_query = any(q in user_query for q in [
                "what car", "which vehicle", "my car", "what vehicle", 
                "what am i driving", "what's my car"
            ])

            # Prepare messages for LLM
            processed_messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": vehicle_context}
            ]
            
            # Add conversation history (excluding previous system messages)
            processed_messages.extend(
                msg for msg in messages 
                if msg["role"] not in ["system", "assistant"] or "Current Vehicle:" not in msg["content"]
            )

            # Generate response
            chat_completion = self.client.chat.completions.create(
                model="gemma2-9b-it",
                messages=processed_messages,
                temperature=0.0,
                max_tokens=1024,
                top_p=0.9
            )
            
            response = chat_completion.choices[0].message.content

            # Remove any special formatting (like **)
            response = re.sub(r'\*\*', '', response)

            # Force vehicle info for vehicle queries
            if is_vehicle_query:
                return f"You have a {vehicle_info}. " + (
                    "How can I help with your vehicle today?" 
                    if "how can i help" not in response.lower() 
                    else ""
                )
            
            return response
        
        except Exception as e:
            logger.error(f"Error in get_diagnosis: {str(e)}")
            return "I encountered a technical error. Please describe your vehicle issue."