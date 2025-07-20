# PDF Q&A Chatbot

A Streamlit-based chatbot that allows users to upload PDF files and ask questions about their content using RAG (Retrieval-Augmented Generation) technology.

## Features

- Upload and process PDF files
- Ask questions about PDF content
- Vector-based similarity search
- Fallback to general knowledge for out-of-scope questions
- Clean and intuitive Streamlit interface
- **Now only answers questions about the currently uploaded PDF (stateless, in-memory, no persistent storage)**
- **Faster: Each upload is processed fresh and previous uploads are not stored or referenced**

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage Notes

- The bot will only answer questions about the PDF you just uploaded. Previous uploads are not stored or accessible.
- Each upload is processed in-memory for speed and privacy.
- No persistent vector database or PDF storage is used.
