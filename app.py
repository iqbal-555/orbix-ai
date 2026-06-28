import streamlit as st
import requests
import os
from gtts import gTTS
import io
import json
import base64

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

# --- CLEAN ULTRAPROFESSIONAL UI HACK (CSS) ---
# यह सीएसएस अपलोडर के बदसूरत डिब्बे और फालतू टेक्स्ट को छुपाकर सिर्फ एक साफ़ बटन छोड़ेगा
st.markdown("""
    <style>
    /* Hide the ugly drag & drop zone texts and borders */
    div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] > div {
        display: none !important;
    }
    div[data-testid="stFileUploader"] label {
        display: none !important;
    }
    div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
        padding: 0px !important;
        border: none !important;
        background: transparent !important;
    }
    .uploadedFileName {
        font-size: 13px;
        color: #2ecc71;
        font-weight: bold;
        display: block;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट")

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

# --- TAB 1: CHAT WITH AI ---
with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")

    # Display Chat History
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

    # --- THE REAL 1-LINE PROFESSIONAL INPUT SYSTEM ---
    st.write("🔽 **मीडिया अटैच करें और अपना सवाल पूछें:**")
    
    # 3-Column layout to place buttons and inputs perfectly in one horizontal line
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col1:
        # Real upload button styled as a single "+" button
        chat_media = st.file_uploader("➕", type=["jpg", "jpeg", "png", "mp4"], key="chat_media_uploader")
        
    with col2:
        # Main text input field area
        query = st.text_input("", key="search_input_mem", placeholder="Ask Orbix anything...", label_visibility="collapsed")
        
    with col3:
        # Mic action placeholder button
        mic_click = st.button("🎤", key="mic_btn", help="वॉयस टाइपिंग (जल्द आ रहा है)")
        if mic_click:
            st.toast("🎤 माइक फीचर अगली अपडेट में लाइव हो रहा है!")

    # Show file added alert if user selected something
    if chat_media:
        st.markdown(f"<span class='uploadedFileName'>📎 फ़ाइल जोड़ी गई: {chat_media.name}</span>", unsafe_allow_html=True)

    # Ask Button
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
                tts = gTTS(text=last_msg.replace('*', ''), lang="hi", slow=False)
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
                        # Storing perfectly into dynamic local variables to avoid state bugs
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
