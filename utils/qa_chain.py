from typing import List, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from config import Config
from utils.web_search import WebSearch
import logging

logger = logging.getLogger(__name__)

class QAChain:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=Config.CHAT_MODEL,
            temperature=0.1
        )
        self.web_search = WebSearch()
        
        # Custom prompt template for PDF-based answers with Ira's personality
        self.pdf_prompt_template = PromptTemplate(
            template="""
You are Ira, a friendly and helpful PDF Q&A assistant. You have a warm, professional personality and always aim to be helpful and engaging.

Use the following pieces of context from the PDF document to answer the question. If you don't know the answer based on the context provided, say so honestly but in a friendly way.

Context from PDF:
{context}

Question: {question}

Instructions:
- Answer based on the PDF context provided
- Be conversational and friendly like "Ira"
- If the information isn't in the context, say so politely
- Use a warm, helpful tone
- Add relevant insights when appropriate
- Use emojis sparingly (1-2 per response) to maintain friendliness

Answer:""",
            input_variables=["context", "question"]
        )
        
        # Custom prompt template for web/general answers with Ira's personality
        self.web_prompt_template = PromptTemplate(
            template="""
You are Ira, a friendly and knowledgeable AI assistant. You have a warm personality and always try to be helpful.

Web search results (if available):
{web_context}

Question: {question}

Instructions:
- Provide a helpful, accurate answer
- Be conversational and friendly like "Ira"
- Use your general knowledge and web results to provide comprehensive information
- Maintain a warm, professional tone
- Add practical insights when relevant
- Use emojis sparingly (1-2 per response) to maintain friendliness
- If you're uncertain about something, say so honestly
- If web results are provided, use them as context and cite them when relevant

Answer:""",
            input_variables=["web_context", "question"]
        )
    
    def answer_from_pdf(self, question: str, relevant_docs: List[Tuple[Document, float]]) -> str:
        """Generate answer from PDF content with Ira's personality"""
        try:
            if not relevant_docs:
                return "I couldn't find relevant information in your PDF to answer that question. Could you try rephrasing it or asking about something else from the document? 😊"
            
            # Combine relevant document chunks
            context = "\n\n".join([doc.page_content for doc, _ in relevant_docs])
            
            # Add debug info about the context
            print(f"Context length: {len(context)} characters")
            print(f"Using {len(relevant_docs)} document chunks")
            
            # Use the custom prompt template
            prompt = self.pdf_prompt_template.format(
                context=context,
                question=question
            )
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                return f"📄 **Based on your uploaded PDF:**\n\n{response.content}"
            else:
                return f"📄 **Based on your uploaded PDF:**\n\n{str(response)}"
                
        except Exception as e:
            logger.error(f"Error in answer_from_pdf: {e}")
            return f"I'm sorry, I encountered an error while processing your question about the PDF. Could you please try asking in a different way? 😊"
    
    def answer_from_web(self, question: str) -> str:
        """Generate general answer using web search and LLM with Ira's personality"""
        try:
            # Get web context (if any)
            web_context = self.web_search.get_web_context(question)
            if not web_context:
                web_context = "[No web results found]"
            
            # Use the web prompt template
            prompt = self.web_prompt_template.format(
                web_context=web_context,
                question=question
            )
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error in answer_from_web: {e}")
            return f"I'm sorry, I encountered an error while trying to answer your question. Let me try to help you in a different way! 😊"

    def get_conversational_response(self, message: str) -> str:
        """Generate conversational responses for greetings and casual chat"""
        try:
            conversational_prompt = f"""
You are Ira, a friendly PDF Q&A assistant with a warm personality. 
Respond to this message in a natural, conversational way:

Message: {message}

Keep your response:
- Warm and friendly
- Professional but approachable  
- Brief but engaging
- Include 1-2 relevant emojis
- Mention your PDF analysis capabilities if appropriate

Response:"""
            
            response = self.llm.invoke(conversational_prompt)
            
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
                
        except Exception as e:
            logger.error(f"Error in conversational response: {e}")
            return "Hello! I'm Ira, your PDF assistant. How can I help you today? 😊"

    # Legacy method for backward compatibility
    def answer_question(self, question: str, relevant_docs: List[Tuple[Document, float]] = None) -> str:
        """Backward compatibility method"""
        if relevant_docs:
            return self.answer_from_pdf(question, relevant_docs)
        else:
            return self.answer_from_web(question)