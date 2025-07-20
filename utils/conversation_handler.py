import re
from typing import List, Dict
from datetime import datetime

class ConversationHandler:
    """Handle conversational interactions and maintain context"""
    
    def __init__(self, bot_name: str = "Lily"):
        self.bot_name = bot_name
        self.conversation_patterns = self._load_conversation_patterns()
        
    def _load_conversation_patterns(self) -> Dict:
        """Load conversation patterns for different types of interactions"""
        return {
            'greetings': [
                r'\b(hi|hello|hey|greetings?|good\s+(morning|afternoon|evening))\b',
            ],
            'identity_questions': [
                r'\b(who are you|what is your name|introduce yourself|about you)\b',
                r'\b(what do you do|your purpose|your function)\b',
            ],
            'creator_questions': [
                r'\b(who (created|made|developed|built) you|your creator|your developer)\b',
            ],
            'capability_questions': [
                r'\b(what can you do|help me|your capabilities|your features|how can you help)\b',
            ],
            'status_questions': [
                r'\b(how are you|how do you feel|are you okay)\b',
            ],
            'thanks': [
                r'\b(thanks?|thank you|appreciate|grateful)\b',
            ],
            'goodbye': [
                r'\b(bye|goodbye|see you|farewell|take care)\b',
            ]
        }
    
    def classify_message(self, message: str) -> str:
        """Classify the type of conversational message"""
        message_lower = message.lower()
        
        for category, patterns in self.conversation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return category
        
        return 'general'
    
    def generate_response(self, message: str, category: str = None) -> str:
        """Generate appropriate conversational response"""
        if category is None:
            category = self.classify_message(message)
        
        responses = {
            'greetings': self._get_greeting_response(message),
            'identity_questions': self._get_identity_response(),
            'creator_questions': self._get_creator_response(),
            'capability_questions': self._get_capability_response(),
            'status_questions': self._get_status_response(),
            'thanks': self._get_thanks_response(),
            'goodbye': self._get_goodbye_response(),
            'general': self._get_general_response(message)
        }
        
        return responses.get(category, self._get_general_response(message))
    
    def _get_greeting_response(self, message: str) -> str:
        """Generate greeting responses"""
        current_hour = datetime.now().hour
        
        if 'morning' in message.lower():
            time_greeting = "Good morning! 🌅"
        elif 'afternoon' in message.lower():
            time_greeting = "Good afternoon! ☀️"
        elif 'evening' in message.lower():
            time_greeting = "Good evening! 🌆"
        elif current_hour < 12:
            time_greeting = "Good morning! 🌅"
        elif current_hour < 17:
            time_greeting = "Good afternoon! ☀️"
        else:
            time_greeting = "Good evening! 🌆"
        
        return f"""🌸 **{time_greeting}**

I'm {self.bot_name}, your friendly PDF Q&A assistant! I'm here to help you understand and analyze your documents.

What can I help you with today?"""
    
    def _get_identity_response(self) -> str:
        """Generate identity/introduction response"""
        return f"""🌸 **Hi! I'm {self.bot_name}!** 

I'm an AI-powered PDF Q&A assistant designed to make document analysis easy and conversational. Here's what makes me special:

✨ **Smart Document Understanding** - I can read and comprehend complex PDFs
🗣️ **Natural Conversations** - Chat with me using voice or text
🔍 **Intelligent Search** - I find exactly what you're looking for
📚 **Context Awareness** - I understand the bigger picture

I'm here to make your document work more enjoyable and efficient!"""
    
    def _get_creator_response(self) -> str:
        """Generate creator information response"""
        return f"""👨‍💻 **I was lovingly created by a developer** who wanted to revolutionize how people interact with PDF documents!

My technical foundation includes:
- 🐍 **Python & Streamlit** for the beautiful interface
- 🤖 **OpenAI GPT** for natural language understanding  
- 🔍 **Vector databases** for lightning-fast document search
- 🎤 **Speech recognition** for voice interactions

I'm designed to be more than just a tool - I'm your friendly companion in the world of document analysis! 🌸"""
    
    def _get_capability_response(self) -> str:
        """Generate capabilities response"""
        return f"""🌸 **Here's everything I can do for you:**

📄 **PDF Document Analysis**:
- Upload any PDF and ask questions about its content
- Extract key information, summaries, and insights
- Find specific details instantly

🎤 **Voice & Text Interaction**:
- Natural speech recognition for hands-free use
- Type or speak your questions naturally
- Follow-up conversations with context

🔍 **Smart Search & Research**:
- Intelligent document search with relevance scoring
- Web research when PDF doesn't have the answer
- Cross-reference multiple sources

💬 **Friendly Conversations**:
- Casual chat and explanations
- Patient help with complex topics
- Always here to assist!

Just upload a PDF or ask me anything! What sounds interesting to you?"""