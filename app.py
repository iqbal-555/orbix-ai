import streamlit as st
import requests
import os
from gtts import gTTS
import io
import json
import base64

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

# --- CUSTOM CSS FOR CLEAN CHAT INTERFACE ---
st.markdown("""
    <style>
    .user-msg { background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #0d47a1; }
    .ai-msg { background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #1b5e20; }
    
    /* Make the file uploader sleek and look like a small plus line */
    div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
        padding: 5px !important;
        border: 1px dashed #1a73e8 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (ऑफिशियल एडिशन)")

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

# --- TAB 1: OFFICIAL MULTIMODAL CHAT ---
with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")
    
    # Display Messages in Container
    chat_placeholder = st.container()
    with chat_placeholder:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

    def get_gemini_multimodal_response(user_query, key, history, media_file=None):
        if not key: return "❌ API Key नहीं मिली।"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        parts = []
        
        if media_file:
            try:
                b64_data = base64.b64encode(media_file.getvalue()).decode("utf-8")
                parts.append({"inlineData": {"mimeType": media_file.type, "data": b64_data}})
            except:
                pass
                
        parts.append({"text": user_query if user_query else "इस फ़ाइल का विश्लेषण करें।"})
        contents = [{"role": "user", "parts": parts}]
        payload = {"contents": contents}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    # --- CHATGPT STYLE INPUT ARCHITECTURE ---
    st.write("---")
    # 1. Clean File Upload Link (Acts as the working '+' attachment node right above the input bar)
    chat_media = st.file_uploader("➕ फोटो या वीडियो जोड़ें (Click to Add Image/Video)", type=["jpg", "jpeg", "png", "mp4"], key="chat_inline_uploader")
    
    # 2. Native Chat Input (Automatically pins to the bottom of the screen on mobile devices)
    if query := st.chat_input("Ask Orbix anything..."):
        with st.spinner("Orbix सोच रहा है..."):
            response_text = get_gemini_multimodal_response(query, DEFAULT_API_KEY, st.session_state.chat_history, chat_media)
            display_text = query if not chat_media else f"📎 [फ़ाइल: {chat_media.name}] {query}"
            st.session_state.chat_history.append({"role": "user", "text": display_text})
            st.session_state.chat_history.append({"role": "model", "text": response_text})
            st.rerun()

    # Voice TTS Output for the latest response
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "model":
        last_msg = st.session_state.chat_history[-1]["text"]
        if not last_msg.startswith("❌"):
            try:
                tts = gTTS(text=last_msg.replace('*', ''), lang="hi", slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.audio(fp, format="audio/mp3")
            except:
                pass

# --- TAB 2: SMART ENTERTAINMENT PLAYER ---
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
                        st.write(f"🎯 वीडियो मिल गया: **{output_lines[0]}**")
                        st.video(f"https://www.youtube.com/watch?v={output_lines[1]}")
                except:
                    st.error("❌ खोजने में समस्या हुई।")

with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("जल्द आ रहा है।")
