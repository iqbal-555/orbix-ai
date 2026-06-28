import streamlit as st
import requests
import os
from gtts import gTTS
import io
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (Play Store Edition)")

# --- SECURE AUTOMATIC API KEY SYSTEM ---
if "GEMINI_API_KEY" in st.secrets:
    DEFAULT_API_KEY = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY")
else:
    DEFAULT_API_KEY = ""

# Sidebar Control Panel
st.sidebar.title("⚙️ Orbix कंट्रोल पैनल")
language = st.sidebar.selectbox("🌐 भाषा चुनें (Select Language)", ["Hindi", "English", "Urdu", "Global"])

if not DEFAULT_API_KEY:
    st.sidebar.warning("⚠️ API Key कॉन्फ़िगर नहीं है। कृपया Secrets सेट करें।")

# Initialize Chat History & States
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

if st.sidebar.button("🧹 चैट इतिहास साफ़ करें"):
    st.session_state.chat_history = []
    st.session_state.voice_text = ""
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Orbix Chat (AI दिमाग)", 
    "🎬 मनोरंजन (Smart Streaming)", 
    "📚 शिक्षा (1st to M.Sc)", 
    "🌾 कृषि टूल (Agriculture AI)"
])

# --- TAB 1: CHAT WITH AI (PROFESSIONAL ONE-LINE INTERFACE) ---
with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")

    # Chat Messages UI
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

    def get_ai_multimodal_response(user_query, key, history):
        if not key: return "❌ API Key नहीं मिली।"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        contents = []
        for chat in history:
            api_role = "user" if chat["role"] == "user" else "model"
            contents.append({"role": api_role, "parts": [{"text": chat["text"]}]})
        contents.append({"role": "user", "parts": [{"text": user_query}]})
        payload = {"contents": contents}
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    # --- ADVANCED JAVASCRIPT VOICETYPING & ONE-LINE DESIGN ---
    # यह इनपुट बॉक्स और माइक को मोबाइल फ्रेंडली और लाइव वर्किंग बनाता है
    st.write("💬 **अपना सवाल लिखें या माइक बटन दबाकर बोलें:**")
    
    # 1. Clean Native File Uploader Section
    chat_media = st.file_uploader("📎 फ़ाइल अपलोडर (Optional)", type=["jpg", "jpeg", "png", "mp4"], key="chat_media_uploader")

    # JavaScript Speech Recognition Component Injection
    # यह सीधे क्रोम ब्राउज़र के माइक को एक्टिवेट करता है
    st.markdown("### 🎙️ वॉइस कमांड कंट्रोल")
    components.html("""
        <div style="display: flex; align-items: center; gap: 10px; font-family: sans-serif;">
            <button id="mic_start_btn" style="background-color: #ff4b4b; color: white; border: none; padding: 12px 20px; border-radius: 20px; font-weight: bold; cursor: pointer;">
                🎤 बोलना शुरू करें
            </button>
            <p id="speech_status" style="margin: 0; color: #666; font-size: 14px;">माइक बंद है</p>
        </div>
        <script>
            const btn = document.getElementById('mic_start_btn');
            const status = document.getElementById('speech_status');
            
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.lang = 'hi-IN'; // Set to Hindi
                recognition.interimResults = false;
                
                btn.onclick = function() {
                    recognition.start();
                    status.innerText = "🔊 सुन रहा हूँ... बोलिए...";
                    btn.style.backgroundColor = "#2ecc71";
                };
                
                recognition.onresult = function(event) {
                    const textResult = event.results[0][0].transcript;
                    status.innerText = "✅ रिकॉर्डेड: " + textResult;
                    btn.style.backgroundColor = "#ff4b4b";
                    
                    // Pass the captured voice text straight to Streamlit hidden elements
                    window.parent.postMessage({
                        type: 'streamlit:set_widget_value',
                        key: 'search_input_mem',
                        value: textResult
                    }, '*');
                };
                
                recognition.onerror = function() {
                    status.innerText = "❌ समझ नहीं आया, दोबारा दबाएं।";
                    btn.style.backgroundColor = "#ff4b4b";
                };
            } else {
                status.innerText = "❌ आपके ब्राउज़र में माइक सपोर्ट नहीं है।";
            }
        </script>
    """, height=60)

    # 2. Standard Text Input Interface that catches Voice or Keyboard typing
    query = st.text_input("", key="search_input_mem", placeholder="यहाँ आपका वॉइस टेक्स्ट आ जाएगा या खुद टाइप करें...")

    if st.button("पूछें 🚀", type="primary", key="send_btn"):
        if query or chat_media:
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_ai_multimodal_response(query, DEFAULT_API_KEY, st.session_state.chat_history)
                display_text = query if query else f"📁 [मीडिया फ़ाइल]"
                st.session_state.chat_history.append({"role": "user", "text": display_text})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                st.rerun()

    # Voice Speech Generator
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
