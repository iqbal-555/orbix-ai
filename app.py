import streamlit as st
import requests
import os
from gtts import gTTS
import io
import subprocess
import json
import base64

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-ジェन बिलियन डॉलर एआई असिस्टेंट (मल्टीमॉडल एडिशन)")

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
    st.sidebar.warning("⚠️ API Key कॉन्फ़िगर नहीं है। कृपया Streamlit Dashboard में Secrets सेट करें।")

# Initialize History & Search State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "search_result" not in st.session_state:
    st.session_state.search_result = None

if st.sidebar.button("🧹 चैट इतिहास साफ़ करें"):
    st.session_state.chat_history = []
    st.session_state.search_result = None
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Orbix Chat (AI दिमाग)", 
    "🎬 मनोरंजन (Smart Streaming)", 
    "📚 शिक्षा (1st to M.Sc)", 
    "🌾 कृषि टूल (Agriculture AI)"
])

# --- TAB 1: CHAT WITH AI (MULTIMODAL WITH MEDIA UPLOADER) ---
with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")
    st.markdown("""
    <style>
    .user-msg { background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #0d47a1; }
    .ai-msg { background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)
    
    # Display Chat History
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

    # Gemini API Call Handler (Handles text and images)
    def get_ai_multimodal_response(user_query, key, history, uploaded_media=None):
        if not key:
            return "❌ API Key नहीं मिली। कृपया Secrets में सेट करें।"
        
        # Use gemini-2.5-flash as it supports text, images, and videos natively
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        
        parts = []
        
        # If user uploaded an image/media, parse it into base64 for Gemini Vision
        if uploaded_media:
            try:
                media_bytes = uploaded_media.getvalue()
                mime_type = uploaded_media.type
                b64_data = base64.b64encode(media_bytes).decode("utf-8")
                parts.append({
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": b64_data
                    }
                })
            except Exception as media_err:
                return f"❌ मीडिया प्रोसेस करने में त्रुटि: {str(media_err)}"
        
        # Append the text query
        parts.append({"text": user_query if user_query else "इस मीडिया (फोटो/वीडियो) का विश्लेषण करें।"})
        
        # Prepare content payload
        contents = []
        # Incorporate historical context if available
        for chat in history:
            api_role = "user" if chat["role"] == "user" else "model"
            contents.append({"role": api_role, "parts": [{"text": chat["text"]}]})
            
        contents.append({"role": "user", "parts": parts})
        payload = {"contents": contents}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"❌ गूगल सर्वर रिस्पॉन्स एरर (कोड {response.status_code})"
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    # --- THE COMPACT CHAT CONTROLS (Input + Media Button) ---
    query = st.text_input("Orbix से कुछ भी पूछें...", key="search_input_mem", placeholder="यहाँ अपना सवाल लिखें या नीचे फ़ाइल अटैच करें...")
    
    # ChatGPT style feature expansion right below input box
    chat_media = st.file_uploader(
        "➕ फोटो या वीडियो जोड़ें (Add Image/Video)", 
        type=["jpg", "jpeg", "png", "mp4", "mov"],
        key="chat_media_uploader",
        help="चैट में फोटो या वीडियो अटैच करने के लिए यहाँ क्लिक करें"
    )
    
    # Live preview right inside the chat window before sending
    if chat_media:
        if "image" in chat_media.type:
            st.image(chat_media, caption="📎 भेजने के लिए तैयार फोटो", width=250)
        elif "video" in chat_media.type:
            st.video(chat_media)

    if st.button("पूछें", type="primary", key="send_btn"):
        if query or chat_media:
            with st.spinner("Orbix देख और सोच रहा है..."):
                # Run multimodal analysis
                response_text = get_ai_multimodal_response(query, DEFAULT_API_KEY, st.session_state.chat_history, chat_media)
                
                # Append to chat list
                display_user_text = query if query else f"📁 [मीडिया फ़ाइल भेजी गई: {chat_media.name}]"
                st.session_state.chat_history.append({"role": "user", "text": display_user_text})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                st.rerun()
        else:
            st.warning("कृपया कुछ टाइप करें या फोटो/वीडियो अपलोड करें।")
            
    # Audio Speech Output for final response
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "model":
        last_msg = st.session_state.chat_history[-1]["text"]
        if not last_msg.startswith("❌"):
            clean_text = last_msg.replace('*', '').replace('#', '')
            tts_lang = "hi" if language == "Hindi" else "en"
            try:
                tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                st.write("🔊 **आखिरी जवाब सुनें:**")
                st.audio(fp, format="audio/mp3")
            except:
                pass

# --- TAB 2: CLEAN HIGH-SPEED STREAMING PLAYER ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन प्लेयर")
    video_name = st.text_input("📝 वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("视频 ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix वीडियो ढूंढ रहा है..."):
                try:
                    command = f'yt-dlp "ytsearch1:{video_name}" --get-id --get-title'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output_lines = result.stdout.strip().split('\n')
                    
                    if len(output_lines) >= 2:
                        st.session_state.search_result = {
                            "title": output_lines[0],
                            "youtube_url": f"https://www.youtube.com/watch?v={output_lines[1]}"
                        }
                        st.rerun()
                    else:
                        st.error("❌ कोई वीडियो नहीं मिला।")
                except Exception as search_err:
                    st.error(f"❌ खोजने में समस्या हुई: {str(search_err)}")

    if st.session_state.search_result:
        res = st.session_state.search_result
        st.success(f"🎯 वीडियो मिल गया: **{res['title']}**")
        st.video(res['youtube_url'])

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल प्रबंधन प्रणालियाँ जल्द आ रही हैं।")
