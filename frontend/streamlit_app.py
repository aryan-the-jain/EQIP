import os
import json
import time
import asyncio
from typing import List, Dict, Any
import streamlit as st
import httpx
from datetime import datetime

# Configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8000")
MAX_CONVERSATION_HISTORY = 5  # Keep last 5 turns

# Page configuration
st.set_page_config(
    page_title="Eqip.ai Chat", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for chat interface
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 0.8rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.user-message {
    background-color: #f0f2f6;
    margin-left: 2rem;
    color: #1f1f1f !important;
}
.assistant-message {
    background-color: #ffffff;
    margin-right: 2rem;
    border-left: 4px solid #007acc;
    color: #1f1f1f !important;
}
.message-header {
    font-weight: bold;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    color: #007acc !important;
}
.message-content {
    line-height: 1.6;
    color: #1f1f1f !important;
}
.message-content h2 {
    color: #007acc !important;
    font-size: 1.1rem;
    margin: 1rem 0 0.5rem 0;
}
.message-content h4 {
    color: #007acc !important;
    font-size: 1rem;
    margin: 0.8rem 0 0.4rem 0;
}
.message-content p {
    color: #1f1f1f !important;
    margin: 0.5rem 0;
}
.message-content ul {
    color: #1f1f1f !important;
}
.message-content li {
    color: #1f1f1f !important;
    margin: 0.3rem 0;
}
.typing-indicator {
    display: flex;
    align-items: center;
    padding: 1rem;
    background-color: #ffffff;
    border-radius: 0.8rem;
    margin-bottom: 1rem;
    margin-right: 2rem;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #007acc;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.typing-dots {
    display: flex;
    gap: 0.25rem;
}
.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #007acc;
    animation: typing 1.4s infinite ease-in-out;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
}
.ip-section {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #007acc;
    color: #1f1f1f !important;
}
.ip-section h4 {
    margin-top: 0;
    color: #007acc !important;
}
.citation {
    font-size: 0.8rem;
    color: #666 !important;
    font-style: italic;
}

/* Override Streamlit's default styles */
.stMarkdown {
    color: #1f1f1f !important;
}
.stMarkdown p {
    color: #1f1f1f !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #007acc !important;
}
.stMarkdown ul li {
    color: #1f1f1f !important;
}
.stMarkdown strong {
    color: #1f1f1f !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables for chat functionality"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "asset_id" not in st.session_state:
        st.session_state.asset_id = None
    if "asset_type" not in st.session_state:
        st.session_state.asset_type = "software"
    if "jurisdictions" not in st.session_state:
        st.session_state.jurisdictions = ["US", "UK"]

def format_message_timestamp() -> str:
    """Generate a formatted timestamp for messages"""
    return datetime.now().strftime("%H:%M")

def add_message(role: str, content: str, metadata: Dict[str, Any] = None):
    """Add a message to the conversation history"""
    message = {
        "role": role,
        "content": content,
        "timestamp": format_message_timestamp(),
        "metadata": metadata or {}
    }
    st.session_state.messages.append(message)
    
    # Keep only the last MAX_CONVERSATION_HISTORY * 2 messages (user + assistant pairs)
    if len(st.session_state.messages) > MAX_CONVERSATION_HISTORY * 2:
        st.session_state.messages = st.session_state.messages[-MAX_CONVERSATION_HISTORY * 2:]

def get_conversation_context() -> List[Dict[str, str]]:
    """Get the last few messages as context for the API call"""
    context = []
    for msg in st.session_state.messages[-MAX_CONVERSATION_HISTORY * 2:]:
        context.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    return context

async def stream_response(question: str, asset_id: int, jurisdictions: List[str]) -> Dict[str, Any]:
    """
    Stream response from the backend API with typing simulation
    Returns the complete response after streaming is done
    """
    # Prepare the payload with conversation context
    context = get_conversation_context()
    payload = {
        "asset_id": asset_id or 1,
        "questions": question,
        "jurisdictions": jurisdictions,
        "conversation_context": context  # Add conversation history
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE}/v1/agents/ip-options",
                json=payload
            )
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise Exception("Request timed out. Please try again.")
    except httpx.RequestError as e:
        raise Exception(f"Connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"API error: {str(e)}")

def display_typing_indicator():
    """Display a typing indicator animation"""
    return st.markdown("""
    <div class="typing-indicator">
        <div class="message-header">🤖 Eqip.ai</div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span>is thinking</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def format_ip_response(response_data: Dict[str, Any]) -> str:
    """Format the IP consultation response into a readable format"""
    formatted_response = ""
    
    # Options section
    if response_data.get("options"):
        formatted_response += "## 🛡️ **IP Protection Options**\n\n"
        for i, option in enumerate(response_data["options"][:3], 1):
            formatted_response += f"{i}. {option}\n\n"
    
    # Risks section
    if response_data.get("risks"):
        formatted_response += "## ⚠️ **Key Risks & Considerations**\n\n"
        for i, risk in enumerate(response_data["risks"][:3], 1):
            formatted_response += f"• {risk}\n\n"
    
    # Next steps section
    if response_data.get("next_steps"):
        formatted_response += "## 📋 **Recommended Next Steps**\n\n"
        for i, step in enumerate(response_data["next_steps"][:3], 1):
            formatted_response += f"{i}. {step}\n\n"
    
    # Citations section
    if response_data.get("citations"):
        formatted_response += "## 📚 **Legal References**\n\n"
        for citation in response_data["citations"][:3]:
            formatted_response += f"• *{citation}*\n\n"
    
    return formatted_response

def display_message(message: Dict[str, Any]):
    """Display a single chat message with proper formatting"""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    metadata = message.get("metadata", {})
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-header">👤 You • {timestamp}</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # For assistant messages, check if we have structured IP data
        if metadata.get("ip_response"):
            formatted_content = format_ip_response(metadata["ip_response"])
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-header">🤖 Eqip.ai • {timestamp}</div>
                <div class="message-content">{formatted_content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="message-header">🤖 Eqip.ai • {timestamp}</div>
                <div class="message-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)

async def handle_user_input(user_input: str):
    """Handle user input and generate streaming response"""
    if not user_input.strip():
        return
    
    # Add user message to chat
    add_message("user", user_input)
    
    # Create placeholder for assistant response
    response_placeholder = st.empty()
    
    # Show typing indicator
    with response_placeholder:
        display_typing_indicator()
    
    try:
        # Simulate typing delay for better UX
        await asyncio.sleep(1)
        
        # Get response from backend
        response_data = await stream_response(
            user_input, 
            st.session_state.asset_id, 
            st.session_state.jurisdictions
        )
        
        # Format the response
        formatted_response = format_ip_response(response_data)
        
        # Add assistant message to chat
        add_message("assistant", formatted_response, {"ip_response": response_data})
        
        # Clear typing indicator and refresh chat
        response_placeholder.empty()
        st.rerun()
        
    except Exception as e:
        # Handle errors gracefully
        error_message = f"I apologize, but I encountered an error: {str(e)}\n\nPlease try again or rephrase your question."
        add_message("assistant", error_message)
        response_placeholder.empty()
        st.rerun()

# Main app
def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.title("🤖 Eqip.ai — Your AI IP Consultant")
    st.markdown("*Get expert intellectual property advice powered by advanced AI and legal knowledge*")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Asset configuration
        st.subheader("Asset Details")
        asset_type = st.selectbox(
            "Asset Type", 
            ["software", "dataset", "media", "invention"],
            index=["software", "dataset", "media", "invention"].index(st.session_state.asset_type)
        )
        st.session_state.asset_type = asset_type
        
        # Jurisdiction selection
        st.subheader("Jurisdictions")
        available_jurisdictions = ["US", "UK", "EU", "CA", "AU", "JP"]
        selected_jurisdictions = st.multiselect(
            "Select jurisdictions of interest",
            available_jurisdictions,
            default=st.session_state.jurisdictions
        )
        if selected_jurisdictions:
            st.session_state.jurisdictions = selected_jurisdictions
        
        # Create asset button
        if st.button("🆕 Create New Asset"):
            try:
                import requests
                response = requests.post(
                    f"{API_BASE}/v1/assets", 
                    json={"type": asset_type, "uri": "", "contributors": []},
                    timeout=10
                )
                if response.status_code == 200:
                    st.session_state.asset_id = response.json()["asset_id"]
                    st.success(f"Created asset #{st.session_state.asset_id}")
                else:
                    st.error("Failed to create asset")
            except Exception as e:
                st.error(f"Error creating asset: {str(e)}")
        
        # Display current asset
        if st.session_state.asset_id:
            st.info(f"Current Asset ID: {st.session_state.asset_id}")
        
        # System status
        st.subheader("System Status")
        try:
            import requests
            health_response = requests.get(f"{API_BASE}/v1/health", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ Backend Online")
            else:
                st.error("❌ Backend Issues")
        except:
            st.error("❌ Backend Offline")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Chat interface
    st.header("💬 IP Consultation Chat")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            # Welcome message
            st.markdown("""
            <div class="chat-message assistant-message">
                <div class="message-header">🤖 Eqip.ai</div>
                <div class="message-content" style="color: #1f1f1f !important;">
                    <p style="color: #1f1f1f !important;">Hello! I'm your AI-powered intellectual property consultant. I can help you with:</p>
                    <br>
                    <ul style="color: #1f1f1f !important;">
                        <li style="color: #1f1f1f !important;"><strong style="color: #007acc !important;">Patent Strategy</strong> - Should you file a patent or keep it as a trade secret?</li>
                        <li style="color: #1f1f1f !important;"><strong style="color: #007acc !important;">Copyright Protection</strong> - How to protect software, content, and creative works</li>
                        <li style="color: #1f1f1f !important;"><strong style="color: #007acc !important;">Trade Secrets</strong> - Best practices for confidential information</li>
                        <li style="color: #1f1f1f !important;"><strong style="color: #007acc !important;">Trademark Guidance</strong> - Brand protection strategies</li>
                        <li style="color: #1f1f1f !important;"><strong style="color: #007acc !important;">Licensing Advice</strong> - IP licensing and commercialization</li>
                    </ul>
                    <br>
                    <p style="color: #1f1f1f !important;">Ask me anything about protecting your intellectual property! 🛡️</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display existing messages
            for message in st.session_state.messages:
                display_message(message)
    
    # Chat input
    st.markdown("---")
    
    # Use columns for better layout
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask your IP question...",
            placeholder="e.g., How should I protect my AI algorithm?",
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 📤", use_container_width=True)
    
    # Handle input submission
    if send_button or (user_input and st.session_state.get("chat_input_submitted")):
        if user_input.strip():
            # Run async function
            asyncio.run(handle_user_input(user_input))
            # Clear input
            st.session_state.chat_input = ""
    
    # Auto-scroll to bottom (simulate with rerun)
    if st.session_state.messages:
        st.markdown('<div id="bottom"></div>', unsafe_allow_html=True)
        st.markdown("""
        <script>
        document.getElementById('bottom').scrollIntoView();
        </script>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
