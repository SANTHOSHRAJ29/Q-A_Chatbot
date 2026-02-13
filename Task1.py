import streamlit as st
import requests
import json
import time
import os
GROQ_API_KEY=os.getenv("api")
MODELS = {
    "Llama 3.3 70B (State of the Art)": "llama-3.3-70b-versatile",
    "Llama 3.1 70B (Versatile)": "llama-3.1-70b-versatile",
    "Llama 3.1 8B (Super Fast)": "llama-3.1-8b-instant",
    "Mixtral 8x7B (Balanced)": "mixtral-8x7b-32768"
}
st.set_page_config(
    page_title="Universal Q&A AI - Assignment 13",
    page_icon="⚡",
    layout="wide"
)
st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #f0f0f0;
    } 
    /* Styled sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input Box Styles */
    .stChatInputContainer {
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Message Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        margin-bottom: 5px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        background: -webkit-linear-gradient(#00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)
def get_groq_streaming_response(messages, model, temperature):
    """Call Groq API with streaming enabled"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
        "stream": True
    }
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').replace('data: ', '')
                if decoded_line == '[DONE]':
                    break
                try:
                    line_json = json.loads(decoded_line)
                    content = line_json['choices'][0]['delta'].get('content', '')
                    if content:
                        full_response += content
                        yield content
                except json.JSONDecodeError:
                    continue
    except requests.exceptions.HTTPError as http_err:
        yield f"🚀 API Error {response.status_code}: {response.text}"
    except Exception as e:
        yield f"⚠️ System Error: {str(e)}"
st.title("⚡ Universal Q&A AI")
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8649/8649595.png", width=80)
    st.header("Settings")
    selected_model_name = st.selectbox("Brain Selection", list(MODELS.keys()), index=0)
    selected_model = MODELS[selected_model_name]
    temp = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
    st.divider()
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("### ✨ Features")
    st.info("- **Fast Inference:** Powered by Groq LPUs\n- **Live Streaming:** Real-time text generation\n- **Context Recall:** Remembers previous messages")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a highly intelligent, helpful, and concise AI assistant. You answer any question accurately and with a professional tone."}
    ]
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_content = ""
        for chunk in get_groq_streaming_response(st.session_state.messages, selected_model, temp):
            full_content += chunk
            response_placeholder.markdown(full_content + "▌")
        response_placeholder.markdown(full_content)
    st.session_state.messages.append({"role": "assistant", "content": full_content})
