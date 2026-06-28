import streamlit as st
import requests
import os
from gtts import gTTS
import io
import subprocess
import json
import base64

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

# --- HIDE STREAMLIT UPLOADER TEXT & BADGES (CSS HACK) ---
# यह सीएसएस कोड 200MB वाले टेक्स्ट और अपलोडर के फालतू लेबल्स को पूरी तरह गायब कर देगा
st.markdown("""
    <style>
    /* Hide the default drag & drop file uploader text and borders */
    div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] > div {
        display: none !important;
    }
    div[data-testid="stFileUploader"] label {
        display: none !important;
    }
    .uploadedFileName {
        font-size: 12px;
        color: #2ecc71;
    }
    
    /* ChatGPT-style Custom Layout Mockup */
    .chatgpt-bar {
        display: flex;
        align-items: center;
        background-color: #f4f4f6;
        border-radius: 25px;
        padding: 8px 15px;
        margin-bottom: 10px;
        border: 1px solid #e1e1e6;
    }
    .chat-icon-left {
        font-size: 20px;
        color: #565869;
        margin-right: 10px;
        cursor: pointer;
    }
    .chat-icon-right {
        font-size: 20px;
        color: #565869;
        margin-left: 10px;
        cursor: pointer;
    }
    .chat-text-mock {
        flex-grow: 1;
        color: #8e8e93;
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (प्रोफेशनल एडिशन)")

# --- SECURE AUTOMATIC API KEY SYSTEM ---
if "GEMINI_API_KEY" in st.secrets:
    DEFAULT_API_KEY = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY")
else:
    DEFAULT_API_KEY = ""

if not DEFAULT_API_KEY:
    st.sidebar.warning("⚠️ API Key कॉन्फ़िगर नहीं है। कृपया Secrets सेट करें।")

# Initialize Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.sidebar.button("🧹 चैट इतिहास साफ़ करें"):
    st.session_state.chat_history = []
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Orbix Chat (AI दिमाग)", 
    "🎬 मनोरंजन (Smart Streaming)", 
    "📚 शिक्षा (1st to M.Sc)", 
    "🌾 कृषि टूल (Agriculture AI)"
])

# --- TAB 1: CHAT WITH AI (CHATGPT STYLE) ---
with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")
    
    # Custom Styled Container for Visualizing ChatGPT Layout
    st.markdown('''
        <div class="chatgpt-bar">
            <div class="chat-icon-left">➕</div>
            <div class="chat-text-mock">Ask Orbix... (नीचे दिए बॉक्स में लिखें या फ़ाइल अटैच करें)</div>
            <div class="chat-icon-right">🎤</div>
        </div>
    ''', unsafe_allow_html=True)

    # Display Chat Messages
    st.markdown("""
    <style>
    .user-msg { background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #0d47a1; }
    .ai-msg { background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)
    
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

    def get_ai_multimodal_response(user_query, key, history, uploaded_media=None):
        if not key: return "❌ API Key नहीं मिली।"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        parts = []
        
        if uploaded_media:
            try:
                b64_data = base64.b64encode(uploaded_media.getvalue()).decode("utf-8")
                parts.append({"inlineData": {"mimeType": uploaded_media.type, "data": b64_data}})
            except:
                pass
        
        parts.append({"text": user_query if user_query else "इस मीडिया का विश्लेषण करें।"})
        contents = [{"role": "user", "parts": parts}]
        payload = {"contents": contents}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    # --- THE CLEAN INPUT SYSTEM ---
    # 1. Clean File Uploader - Displays ONLY the small standard button now
    chat_media = st.file_uploader("", type=["jpg", "jpeg", "png", "mp4"], key="chat_media_uploader")
    
    if chat_media:
        st.markdown(f"<span class='uploadedFileName'>📎 फ़ाइल जोड़ी गई: {chat_media.name}</span>", unsafe_allow_html=True)

    # 2. Direct Text Input
    query = st.text_input("", key="search_input_mem", placeholder="यहाँ अपना सवाल लिखें...")

    if st.button("पूछें 🚀", type="primary", key="send_btn"):
        if query or chat_media:
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_ai_multimodal_response(query, DEFAULT_API_KEY, st.session_state.chat_history, chat_media)
                display_text = query if query else f"📁 [मीडिया: {chat_media.name}]"
                st.session_state.chat_history.append({"role": "user", "text": display_text})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                st.rerun()

    # Voice TTS Output
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "model":
        last_msg = st.session_state.chat_history[-1]["text"]
        if not last_msg.startswith("❌"):
            try:
                tts = gTTS(text=last_msg.replace('*', ''), lang="hi" if language == "Hindi" else "en", slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp, format="audio/mp3")
            except:
                pass

# --- TAB 2: CLEAN HIGH-SPEED STREAMING PLAYER ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन प्लेयर")
    video_name = st.text_input("📝 वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix वीडियो ढूंढ रहा है..."):
                try:
                    command = f'yt-dlp "ytsearch1:{video_name}" --get-id --get-title'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output_lines = result.stdout.strip().split('\n')
                    if len(output_lines) >= 2:
                        st.session_state.search_result = {"title": output_lines[0], "youtube_url": f"https://www.youtube.com/watch?v={output_lines[1]}"}
                        st.rerun()
                except:
                    st.error("❌ खोजने में समस्या हुई।")

    if st.session_state.search_result:
        st.success(f"🎯 वीडियो मिल गया: **{st.session_state.search_result['title']}**")
        st.video(st.session_state.search_result['youtube_url'])

with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("जल्द आ रहा है।")
