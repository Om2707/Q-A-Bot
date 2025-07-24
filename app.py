import streamlit as st
import os
from utils.pdf_processor import PDFProcessor
from utils.vector_store import VectorStore
from utils.qa_chain import QAChain
from utils.web_search import WebSearch
from config import Config
import tempfile
from io import BytesIO
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Ira - PDF Q&A Chatbot",
    page_icon="🌸",
    layout="wide"
)

# Initialize components
@st.cache_resource
def initialize_components():
    return {
        'pdf_processor': PDFProcessor(),
        'vector_store': VectorStore(),
        'qa_chain': QAChain(),
        'web_search': WebSearch()
    }

def is_conversational_query(question):
    """Check if the question is conversational/greeting rather than PDF-related"""
    conversational_patterns = [
        r'\b(hi|hello|hey|greetings?)\b',
        r'\bwho are you\b',
        r'\bwhat is your name\b',
        r'\bwho created you\b',
        r'\bwho made you\b',
        r'\bwho developed you\b',
        r'\bhow are you\b',
        r'\bwhat can you do\b',
        r'\bhelp me\b',
        r'\bwhat are your capabilities\b',
        r'\bintroduce yourself\b',
        r'\babout you\b',
        r'\byour features\b',
        r'\bgood morning\b',
        r'\bgood afternoon\b',
        r'\bgood evening\b',
        r'\bthanks?\b',
        r'\bthank you\b',
        r'\bbye\b',
        r'\bgoodbye\b',
        r'\bsee you\b',
    ]
    
    question_lower = question.lower()
    return any(re.search(pattern, question_lower, re.IGNORECASE) for pattern in conversational_patterns)

def generate_conversational_response(question):
    """Generate conversational responses for greetings and general questions"""
    question_lower = question.lower()
    
    # Greetings
    if re.search(r'\b(hi|hello|hey|greetings?)\b', question_lower):
        return """🌸 **Hello! I'm Ira, your friendly PDF Q&A assistant!** 👋

I'm here to help you understand and analyze your PDF documents. Here's what I can do:

📄 **PDF Analysis**: Upload a PDF and I'll help you find specific information
🔍 **Smart Search**: I can search through your documents intelligently  
🎤 **Voice Support**: You can ask questions using voice input
💬 **General Chat**: We can have casual conversations too!

How can I assist you today?"""

    # Self-introduction
    elif re.search(r'\b(who are you|what is your name|introduce yourself|about you)\b', question_lower):
        return """🌸 **I'm Ira!** 

I'm an AI-powered PDF Q&A chatbot designed to help you interact with your documents in a natural way. I can:

✨ **Understand** complex PDF documents
🧠 **Answer** questions about their content  
🎯 **Find** specific information quickly
🗣️ **Chat** naturally using voice or text
📚 **Learn** from the documents you upload

I'm always ready to help make your document analysis easier and more enjoyable!"""

    # Creator information
    elif re.search(r'\b(who created you|who made you|who developed you)\b', question_lower):
        return """👨‍💻 **I was created by a Om Sir** who wanted to make PDF analysis more accessible and conversational!

I'm built using:
- 🐍 **Python & Streamlit** for the interface
- 🤖 **OpenAI GPT** for natural language understanding
- 🔍 **Vector databases** for smart document search
- 🎤 **Speech recognition** for voice interaction

My purpose is to bridge the gap between complex documents and easy understanding. I'm here to make your document work more efficient and enjoyable! 🌸"""

    # Capabilities
    elif re.search(r'\b(what can you do|help me|your capabilities|your features)\b', question_lower):
        return """🌸 **Here's what I can help you with:**

📄 **Document Analysis**:
- Upload PDF files and ask questions about their content
- Extract key information and summaries
- Find specific details quickly

🎤 **Voice Interaction**:
- Ask questions using voice input
- Natural speech recognition
- Hands-free document exploration

💬 **Smart Conversations**:
- Answer questions in natural language
- Provide context-aware responses
- Handle follow-up questions

🔍 **Search & Research**:
- Intelligent document search
- Web-based research when needed
- Cross-reference information

Just upload a PDF and start asking questions, or we can continue chatting! What would you like to try?"""

    # How are you
    elif re.search(r'\bhow are you\b', question_lower):
        return """🌸 **I'm doing great, thank you for asking!** 

I'm running smoothly and ready to help you with any PDF documents or questions you might have. My systems are all green and I'm excited to assist you today!

How are you doing? Is there a document you'd like to analyze or anything else I can help with? 😊"""

    # Thanks
    elif re.search(r'\b(thanks?|thank you)\b', question_lower):
        return """🌸 **You're very welcome!** 

I'm always happy to help! If you have any PDF documents to analyze or more questions, just let me know. I'm here whenever you need assistance! 😊"""

    # Goodbye
    elif re.search(r'\b(bye|goodbye|see you)\b', question_lower):
        return """🌸 **Goodbye! It was lovely chatting with you!** 👋

Feel free to come back anytime you need help with PDF documents or just want to chat. I'll be here waiting to assist you!

Have a wonderful day! 🌟"""

    # Time-based greetings
    elif re.search(r'\b(good morning|good afternoon|good evening)\b', question_lower):
        current_hour = datetime.now().hour
        if current_hour < 12:
            time_response = "Good morning! 🌅"
        elif current_hour < 17:
            time_response = "Good afternoon! ☀️"
        else:
            time_response = "Good evening! 🌆"
            
        return f"""🌸 **{time_response}**

I hope you're having a great day! I'm Ira, ready to help you with any PDF documents or questions you might have.

What can I assist you with today?"""

    # Default conversational response
    else:
        return """🌸 **I'm Ira, your PDF Q&A assistant!** 

I'd love to help you with that! While I'm great at analyzing PDF documents and answering questions about them, I can also have general conversations.

If you have a PDF document you'd like to explore, just upload it and start asking questions. Otherwise, feel free to ask me anything else!

What would you like to know or discuss? 😊"""

def main():
    st.title("🌸 Ira - Your PDF Q&A Assistant")
    st.markdown("*Upload a PDF and chat with me about its content, or just say hello!* 💬")
    
    # Hide the "Deploy" button from the Streamlit toolbar
    st.markdown("""
        <style>
        .stDeployButton {
            visibility: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if OpenAI API key is set, prioritizing Streamlit secrets
    openai_api_key = None
    
    # Manually check for secrets.toml to avoid Streamlit's FileNotFoundError message
    secrets_paths = [
        os.path.join(os.path.expanduser("~"), ".streamlit/secrets.toml"),
        ".streamlit/secrets.toml"
    ]
    secrets_file_exists = any(os.path.exists(p) for p in secrets_paths)

    if secrets_file_exists:
        try:
            if "OPENAI_API_KEY" in st.secrets:
                openai_api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            # If st.secrets fails for any reason, we can fall back silently
            pass
    
    if not openai_api_key:
        # Fallback to environment variable if not in secrets
        openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        st.error("⚠️ Please set your OpenAI API key.")
        st.info("You can add it to `.streamlit/secrets.toml` for deployment or set it as an environment variable for local development.")
        st.code("OPENAI_API_KEY = 'your_api_key_here'", language="toml")
        st.stop()

    Config.OPENAI_API_KEY = openai_api_key
    
    # Initialize components
    components = initialize_components()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": """🌸 **Hello! I'm Ira, your friendly PDF Q&A assistant!** 👋

I'm excited to help you explore and understand your documents. You can:
- Upload a PDF and ask questions about it 📄
- Chat with me using voice or text 💬
- Ask me about my capabilities 🤖

What would you like to do today?"""
            }
        ]
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'current_pdf' not in st.session_state:
        st.session_state.current_pdf = None
    if 'debug_info' not in st.session_state:
        st.session_state.debug_info = []
    if 'last_uploaded_pdf' not in st.session_state:
        st.session_state.last_uploaded_pdf = None
    if 'show_upload_success' not in st.session_state:
        st.session_state.show_upload_success = False

    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📄 Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF file to ask questions about its content"
        )

        # Process PDF when uploaded
        if uploaded_file is not None:
            if uploaded_file.name != st.session_state.last_uploaded_pdf:
                process_pdf(uploaded_file, components)
                st.session_state.last_uploaded_pdf = uploaded_file.name
                st.session_state.show_upload_success = True

        # Show upload success message
        if st.session_state.get('show_upload_success', False):
            st.success("PDF uploaded successfully!")
            st.session_state.show_upload_success = False

        # Display current PDF info and controls
        if st.session_state.pdf_processed:
            st.info(f"📄 Current PDF: {st.session_state.current_pdf}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", help="Clear chat history"):
                    st.session_state.messages = [
                        {
                            "role": "assistant", 
                            "content": "🌸 **Chat cleared!** I'm still here and ready to help with your PDF or any other questions! 😊"
                        }
                    ]
                    st.rerun()
            
            with col2:
                if st.button("🔄 Reset All", help="Clear everything"):
                    st.session_state.messages = [
                        {
                            "role": "assistant", 
                            "content": "🌸 **All reset!** Feel free to upload a new PDF or just chat with me! How can I help you today? 😊"
                        }
                    ]
                    st.session_state.pdf_processed = False
                    st.session_state.current_pdf = None
                    st.session_state.last_uploaded_pdf = None
                    st.rerun()

        # About Ira section
        with st.expander("🌸 About Ira"):
            st.markdown("""
            **I'm Ira**, your intelligent PDF assistant! I can:
            - 📄 Analyze PDF documents
            - 🔍 Answer questions about content
            - 🎤 Understand voice input
            - 💬 Have natural conversations
            - 🧠 Provide smart insights
            
            Just upload a PDF or start chatting!
            """)

        # Debug toggle
        if st.session_state.get('debug_info'):
            show_debug = st.checkbox("Show Debug Info", value=False)
            if show_debug:
                with st.expander("Debug Information"):
                    for debug_msg in st.session_state.debug_info[-10:]:
                        st.text(debug_msg)

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Input section with voice and text support
    st.markdown("---")
    
    # Voice input section
    st.subheader("🎤 Voice Input")
    voice_col1, voice_col2 = st.columns([3, 1])
    
    with voice_col1:
        try:
            from streamlit_mic_recorder import speech_to_text
            
            voice_text = speech_to_text(
                start_prompt="🎤 Start Recording",
                stop_prompt="⏹️ Stop Recording", 
                just_once=True,
                use_container_width=True,
                key="voice_input"
            )
            
            if voice_text:
                process_user_input(voice_text, components, chat_container)
                
        except ImportError:
            st.info("📦 Install `streamlit-mic-recorder` for voice input support:")
            st.code("pip install streamlit-mic-recorder", language="bash")
    
    with voice_col2:
        st.markdown("**OR**")
    
    # Text input section
    st.subheader("⌨️ Text Input")
    with st.form(key="question_form", clear_on_submit=True):
        text_input = st.text_input(
            "Chat with Ira:",
            placeholder="Hi Ira! or Ask about your PDF...",
            key="text_question"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            text_submit = st.form_submit_button("Send 📤", use_container_width=True)
        with col2:
            clear_input = st.form_submit_button("Clear 🗑️", use_container_width=True)
        
        if text_submit and text_input.strip():
            process_user_input(text_input.strip(), components, chat_container)
        
        if clear_input:
            st.rerun()

def process_pdf(uploaded_file, components):
    """Process uploaded PDF file"""
    try:
        with st.spinner("🔄 Processing PDF..."):
            if uploaded_file.size > Config.MAX_FILE_SIZE:
                st.error(f"❌ File size exceeds {Config.MAX_FILE_SIZE // (1024*1024)}MB limit")
                return

            filename = uploaded_file.name
            pdf_bytes = uploaded_file.getbuffer()
            text_chunks = components['pdf_processor'].process_pdf_bytes(BytesIO(pdf_bytes))

            if not text_chunks:
                st.error("❌ No text content found in PDF. Please ensure the PDF contains extractable text.")
                return

            components['vector_store'].create_vector_store(text_chunks, filename)
            st.session_state.pdf_processed = True
            st.session_state.current_pdf = filename
            st.session_state.debug_info.append(f"PDF processed successfully: {filename}")
            
            # Add a message about successful PDF processing
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"🌸 **Perfect! I've processed your PDF: '{filename}'** 📄\n\nNow I can answer questions about its content! What would you like to know about this document?"
            })
            
    except Exception as e:
        error_msg = f"Error processing PDF: {str(e)}"
        st.error(f"❌ {error_msg}")
        st.session_state.debug_info.append(error_msg)

def process_user_input(user_input, components, chat_container):
    """Process user input and generate appropriate response"""
    if not user_input or not user_input.strip():
        return
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)
    
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                # Check if it's a conversational query first
                if is_conversational_query(user_input):
                    response = generate_conversational_response(user_input)
                else:
                    # Handle PDF-related or general questions
                    response = generate_response(user_input, components)
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

def generate_response(question, components):
    """Generate response to user question"""
    try:
        debug_msg = f"Processing question: {question}"
        st.session_state.debug_info.append(debug_msg)
        
        if st.session_state.pdf_processed:
            relevant_docs = components['vector_store'].similarity_search(question, k=3)
            debug_msg = f"Found {len(relevant_docs)} relevant documents"
            st.session_state.debug_info.append(debug_msg)
            
            if relevant_docs:
                for i, (doc, score) in enumerate(relevant_docs):
                    score_msg = f"Doc {i+1}: Score={score:.4f}"
                    st.session_state.debug_info.append(score_msg)
            
            is_relevant = components['vector_store'].is_relevant_to_pdf(question)
            relevance_msg = f"Question relevance to PDF: {is_relevant}"
            st.session_state.debug_info.append(relevance_msg)
            
            if is_relevant and relevant_docs:
                response = components['qa_chain'].answer_from_pdf(question, relevant_docs)
                return f"🌸 **From your PDF '{st.session_state.current_pdf}':**\n\n{response}"
            else:
                if not relevant_docs:
                    reason = "No relevant content found in PDF"
                    chunk_preview = ""
                else:
                    best_score = relevant_docs[0][1]
                    reason = f"PDF content not sufficiently relevant (similarity: {best_score:.3f})"
                    chunk_preview = f"\n\n📋 **Most similar PDF section:**\n> {relevant_docs[0][0].page_content[:300]}..."
                
                web_response = components['qa_chain'].answer_from_web(question)
                return f"""🌸 **Here's what I know about that:**

{web_response}

---
ℹ️ *{reason}*{chunk_preview}

💡 *For PDF-specific answers, try asking questions directly about your document content!*"""
        else:
            # No PDF uploaded, provide general answer
            web_response = components['qa_chain'].answer_from_web(question)
            return f"""🌸 **Here's what I can tell you:**

{web_response}

---
💡 *Upload a PDF document to get specific answers about its content!*"""
            
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        st.session_state.debug_info.append(error_msg)
        return f"🌸 **Oops!** I encountered an error: {str(e)}\n\nCould you please try rephrasing your question? I'm here to help! 😊"

if __name__ == "__main__":
    main()