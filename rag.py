import os
import json
from pymongo import MongoClient
import anthropic
import numpy as np
from typing import List, Dict, Any
import streamlit as st
from datetime import datetime
import requests

class MedDRARAGChatbot:
    def __init__(self):
        # Initialize MongoDB connection
        self.mongo_uri = "TODO - MONGODB CONNECTION STRING"
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client["med"]
        self.collection = self.db["meddra"]
        
        # Initialize Claude client
        self.claude_client = anthropic.Anthropic(
            api_key="TODO - ANTHROPIC API KEY"
        )
        
        # Vector search index name in MongoDB Atlas
        self.vector_index_name = "meddra"
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for the input text"""
        api_key = "TODO - VOYAGE API KEY"

        # Voyage AI API endpoint for embeddings
        url = "https://api.voyageai.com/v1/embeddings"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "voyage-3-large",
            "input": text,
            "input_type": "query" # Can be "query" or "document" depending on your use case
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            request_result = response.json()
            embedding = request_result.get("data", [{}])[0].get("embedding", [])
            return embedding
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None
    
    def vector_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform vector search in MongoDB Atlas"""
        query_embedding = self.generate_embedding(query)
        
        # MongoDB Atlas Vector Search aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.vector_index_name,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "llt_name": 1,
                    "llt_code": 1,
                    "pt_name": 1,
                    "pt_code": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results into readable context"""
        if not results:
            return "No relevant medical terms found."
        
        context = "Relevant medical terms from MedDRA dictionary:\\n\\n"
        
        for i, result in enumerate(results, 1):
            context += f"{i}. **{result['pt_name']}** (Code: {result['pt_code']})\\n"
            if result['llt_name'] != result['pt_name']:
                context += f"   - Also known as: {result['llt_name']} (Code: {result['llt_code']})\\n"
            context += f"   - Relevance Score: {result['score']:.3f}\\n\\n"
        
        return context
    
    def generate_response(self, user_query: str, context: str) -> str:
        """Generate response using Claude with RAG context"""
        
        system_prompt = """You are a medical terminology assistant specializing in MedDRA (Medical Dictionary for Regulatory Activities) terms. You help users understand medical terms, their relationships, and provide accurate information about adverse events and medical conditions.

Key guidelines:
- Use the provided MedDRA context to answer questions accurately
- Explain medical terms in both clinical and lay language when appropriate
- Mention MedDRA codes when relevant
- If the context doesn't contain relevant information, say so clearly
- Always emphasize that this is for informational purposes only and not medical advice
- Be precise about terminology relationships (PT vs LLT)"""

        user_prompt = f"""Based on the following MedDRA dictionary context, please answer the user's question:

CONTEXT:
{context}

USER QUESTION: {user_query}

Please provide a helpful, accurate response based on the MedDRA terms provided in the context."""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self, user_query: str) -> Dict[str, Any]:
        """Main chat function that combines vector search and LLM response"""
        # Perform vector search
        search_results = self.vector_search(user_query, limit=5)
        
        # Format context
        context = self.format_search_results(search_results)
        
        # Generate response
        response = self.generate_response(user_query, context)
        
        return {
            "query": user_query,
            "search_results": search_results,
            "context": context,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Streamlit app interface"""
    st.set_page_config(
        page_title="MedDRA RAG Chatbot",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 MedDRA Medical Terms RAG Chatbot")
    st.markdown("*Ask questions about medical terms and adverse events using MedDRA dictionary*")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = MedDRARAGChatbot()
            st.success("✅ Connected to MongoDB Atlas and Claude API")
        except Exception as e:
            st.error(f"❌ Error initializing chatbot: {str(e)}")
            st.stop()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar with example queries
    with st.sidebar:
        st.header("💡 Example Queries")
        example_queries = [
            "What is a headache in medical terms?",
            "Show me different types of pain terms",
            "What are gastrointestinal side effects?",
            "Tell me about nausea and vomiting",
            "What's the difference between diarrhea and diarrhoea?",
            "Show me heart-related adverse events",
            "What are psychiatric adverse events?"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.current_query = query
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # User input
        user_input = st.text_input(
            "Ask about medical terms:",
            value=st.session_state.get('current_query', ''),
            placeholder="e.g., What are the different types of headaches?"
        )
        
        if st.button("Send", type="primary") or user_input:
            if user_input.strip():
                with st.spinner("Searching MedDRA database and generating response..."):
                    # Get response from chatbot
                    result = st.session_state.chatbot.chat(user_input)
                    
                    # Add to chat history
                    st.session_state.chat_history.append(result)
                    
                    # Clear current query
                    if 'current_query' in st.session_state:
                        del st.session_state.current_query
        
        # Display chat history
        st.header("💬 Chat History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['query'][:50]}...", expanded=(i==0)):
                st.markdown(f"**Query:** {chat['query']}")
                st.markdown(f"**Response:**\\n{chat['response']}")
                
                # Show search results
                if chat['search_results']:
                    st.markdown("**Relevant MedDRA Terms:**")
                    for result in chat['search_results']:
                        st.markdown(f"- **{result['pt_name']}** (PT: {result['pt_code']})")
                        if result['llt_name'] != result['pt_name']:
                            st.markdown(f"  - LLT: {result['llt_name']} ({result['llt_code']})")
                        st.markdown(f"  - Score: {result['score']:.3f}")
                
                st.markdown(f"*{chat['timestamp']}*")
    
    with col2:
        st.header("🔧 Configuration")
        
        # Environment variables info
        st.markdown("**Required Environment Variables:**")
        st.code("""
MONGODB_URI=your_mongodb_atlas_connection_string
MONGODB_DATABASE=medical_data
MONGODB_COLLECTION=meddra
ANTHROPIC_API_KEY=your_claude_api_key
VECTOR_INDEX_NAME=vector_index
        """)
        
        # Database stats
        if st.button("Check Database Connection"):
            try:
                count = st.session_state.chatbot.collection.count_documents({})
                st.success(f"✅ Connected! Found {count} documents")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
        
        # Clear chat history
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")

# CLI version for testing
def cli_interface():
    """Command line interface for testing"""
    print("MedDRA RAG Chatbot - CLI Mode")
    print("Type 'quit' to exit\\n")
    
    chatbot = MedDRARAGChatbot()
    
    while True:
        user_input = input("\\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        print("\\nSearching...")
        result = chatbot.chat(user_input)
        
        print(f"\\nBot: {result['response']}")
        
        # Show search results
        if result['search_results']:
            print("\\n--- Relevant MedDRA Terms ---")
            for res in result['search_results']:
                print(f"• {res['pt_name']} (PT: {res['pt_code']}) - Score: {res['score']:.3f}")

if __name__ == "__main__":
    # Check if running in Streamlit
    try:
        import streamlit as st
        main()
    except ImportError:
        # Fall back to CLI if Streamlit not available
        cli_interface()