import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Optional
    
    # Vector store settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # OpenAI settings
    EMBEDDING_MODEL = "text-embedding-ada-002"
    CHAT_MODEL = "gpt-3.5-turbo"
    
    # File paths
    UPLOAD_DIR = "data/uploads"
    VECTOR_DB_DIR = "data/vector_db"
    
    # App settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    # FIXED: For ChromaDB distance scores, lower threshold = more strict
    # ChromaDB returns distance scores where 0 = perfect match, higher = less similar
    SIMILARITY_THRESHOLD = 0.5  # Reduced from 0.7 to be more lenient
    
    # Chatbot personality settings
BOT_NAME = "Lily"
BOT_PERSONALITY = "friendly, helpful, and professional PDF Q&A assistant"
GREETING_MESSAGE = "Hello! I'm Lily, your friendly PDF Q&A assistant! How can I help you today?"

# Conversation settings  
ENABLE_CONVERSATIONAL_MODE = True
CONVERSATION_CONTEXT_LENGTH = 5  # Number of previous messages to remember