import streamlit as st
import requests
import os
from gtts import gTTS
import io
import subprocess
import json

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट")

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
    "🎬 मनोरंजन (Streaming & Download)", 
    "📚 शिक्षा (1st to M.Sc)", 
    "🌾 कृषि टूल (Agriculture AI)"
])

# --- TAB 1: CHAT WITH AI ---
with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")
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

    def get_ai_response_with_memory(user_query, key, history):
        if not key:
            return "❌ API Key नहीं मिली। कृपया अपने Streamlit Advanced Settings में Secrets जोड़ें।"
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
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"❌ गूगल सर्वर रिस्पॉन्स एरर।"
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    query = st.text_input("Orbix से कुछ भी पूछें...", key="search_input_mem")
    if st.button("पूछें", type="primary", key="send_btn"):
        if query:
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_ai_response_with_memory(query, DEFAULT_API_KEY, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "user", "text": query})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                st.rerun()
            
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

# --- TAB 2: STREAMING & BROWSER-DIRECT HD VIDEO DOWNLOAD (100% SUCCESSRATE) ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन सर्च")
    st.write("यहाँ गाने का नाम लिखें। Orbix उसे 1-क्लिक में आपके ब्राउज़र से सीधे डाउनलोड कराएगा!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix इंटरनेट पर वीडियो ढूंढ रहा है..."):
                try:
                    command = f'yt-dlp "ytsearch1:{video_name}" --dump-json'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        video_data = json.loads(result.stdout)
                        
                        # Find combined formats containing both high quality video and audio
                        best_direct_url = None
                        for fmt in video_data.get('formats', []):
                            # Format 22 is perfect for direct unblocked 720p HD progressive stream
                            if fmt.get('format_id') == '22' and fmt.get('url'):
                                best_direct_url = fmt['url']
                                break
                        
                        # Fallback to general best progressive stream if 22 isn't standalone
                        if not best_direct_url:
                            for fmt in video_data.get('formats', []):
                                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('url'):
                                    best_direct_url = fmt['url']
                                    if fmt.get('height', 0) >= 480:
                                        break
                        
                        st.session_state.search_result = {
                            "title": video_data.get('title', 'Video'),
                            "youtube_url": f"https://www.youtube.com/watch?v={video_data.get('id', '')}",
                            "download_url": best_direct_url or video_data.get('url')
                        }
                        st.rerun()
                    else:
                        st.error("❌ कोई वीडियो नहीं मिला।")
                except Exception as search_err:
                    st.error(f"❌ खोजने में समस्या हुई: {str(search_err)}")

    if st.session_state.search_result:
        res = st.session_state.search_result
        st.success(f"🎯 वीडियो मिल गया: **{res['title']}**")
        
        # Play Video in App
        st.video(res['youtube_url'])
        
        st.write("---")
        st.subheader("📥 डायरेक्ट 1-क्लिक ब्राउज़र डाउनलोड")
        st.write("नीचे दिए गए लाल बटन पर क्लिक करें। आपके मोबाइल का डिफ़ॉल्ट डाउनलोड मैनेजर इसे बिना किसी एरर के तुरंत डाउनलोड कर लेगा:")
        
        if res['download_url']:
            # Using HTML Anchor link with download attributes to let the client browser download directly.
            # This completely avoids server-side crashes, memory freezes, and download failed issues!
            st.markdown(f'''
                <div style="margin-top: 10px;">
                    <a href="{res['download_url']}" target="_blank" download="{res['title']}.mp4">
                        <button style="background-color: #ff4b4b; color: white; padding: 15px 30px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; width: 100%;">
                            🔥 सीधे अपने मोबाइल में डाउनलोड करें (Instant Browser Download)
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
            st.caption("✨ **नोट:** बटन दबाते ही आपके ब्राउज़र में वीडियो का डायरेक्ट डाउनलोड शुरू हो जाएगा। अगर कोई नया प्लेयर पेज खुले, तो वहाँ कोने में 3 डॉट्स (⋮) दबाकर Download चुन लें।")
        else:
            st.error("❌ डाउनलोड लिंक जनरेट नहीं हो सका।")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
