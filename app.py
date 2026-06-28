import streamlit as st
import requests
import os
from gtts import gTTS
import io
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (अल्ट्रा-मल्टीमॉडल)")

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

# --- TAB 1: GEMINI & CHATGPT LOOK INTERFACE ---
with tab1:
    st.markdown("""
    <style>
    .user-msg { background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #0d47a1; }
    .ai-msg { background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #1b5e20; }
    /* Hide native Streamlit input blocks to maintain strict bottom UI control */
    div[data-testid="stFileUploader"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Render Chat History
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

    def get_gemini_response(user_query, key, history):
        if not key: return "❌ API Key Missing!"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        contents = []
        for chat in history:
            role_type = "user" if chat["role"] == "user" else "model"
            contents.append({"role": role_type, "parts": [{"text": chat["text"]}]})
        contents.append({"role": "user", "parts": [{"text": user_query}]})
        
        try:
            res = requests.post(url, headers=headers, json={"contents": contents})
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"❌ Error: {str(e)}"

    # Catching backend triggers from the custom HTML bar
    params = st.query_params
    if "msg" in params:
        user_input = params["msg"]
        # Clear query params instantly to prevent loop triggers
        st.query_params.clear()
        with st.spinner("Orbix सोच रहा है..."):
            ai_reply = get_gemini_response(user_input, DEFAULT_API_KEY, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            st.session_state.chat_history.append({"role": "model", "text": ai_reply})
            st.rerun()

    # --- ADVANCED FIXED BOTTOM CHATGPT/GEMINI INPUT BAR ---
    components.html("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #ffffff; padding: 10px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 8px; z-index: 99999; font-family: sans-serif;">
            <button id="plus_btn" style="background: none; border: none; font-size: 24px; color: #1a73e8; cursor: pointer; padding: 5px;">+</button>
            <input id="chat_input" type="text" placeholder="Ask Orbix..." style="flex-grow: 1; border: 1px solid #dadce0; padding: 12px 15px; border-radius: 24px; font-size: 16px; outline: none;" />
            <button id="mic_btn" style="background: none; border: none; font-size: 22px; color: #5f6368; cursor: pointer; padding: 5px;">🎤</button>
            <button id="send_btn" style="background: #1a73e8; border: none; color: white; padding: 10px 16px; border-radius: 50%; font-weight: bold; cursor: pointer; font-size: 16px;">➔</button>
        </div>
        
        <script>
            const inputField = document.getElementById('chat_input');
            const sendBtn = document.getElementById('send_btn');
            const micBtn = document.getElementById('mic_btn');
            const plusBtn = document.getElementById('plus_btn');

            // 1. Native Real-time Speech Recognition Protocol
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.lang = 'hi-IN'; // Default Hindi support
                recognition.interimResults = false;

                micBtn.onclick = function() {
                    recognition.start();
                    micBtn.style.color = "#ea4335"; // Turns red when active
                    inputField.placeholder = "🔊 Sun raha hoon, boliye...";
                };

                recognition.onresult = function(event) {
                    const text = event.results[0][0].transcript;
                    inputField.value = text;
                    micBtn.style.color = "#5f6368";
                    inputField.placeholder = "Ask Orbix...";
                };

                recognition.onerror = function() {
                    micBtn.style.color = "#5f6368";
                    inputField.placeholder = "Mic Error, try again...";
                };
            }

            // Plus trigger placeholder action
            plusBtn.onclick = function() {
                alert("📎 Gallery feature coming soon in mobile wrapper app!");
            };

            // 2. Transmit message safely to Streamlit processing pipeline
            function submitMessage() {
                const text = inputField.value.trim();
                if(text) {
                    // Inject text directly into URL query parameters to force safe fast processing
                    window.parent.location.search = "?msg=" + encodeURIComponent(text);
                }
            }

            sendBtn.onclick = submitMessage;
            inputField.addEventListener("keypress", function(e) {
                if (e.key === "Enter") { submitMessage(); }
            });
        </script>
    """, height=70)

    # Voice Speech TTS Generator
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
