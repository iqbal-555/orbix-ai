import streamlit as st
import requests
import os
from gtts import gTTS
import io
import subprocess
import json

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (ग्लोबल एडिशन)")

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
    "🎬 मनोरंजन (ग्लोबल HD 1-Click Download)", 
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

# --- TAB 2: STREAMING & UNIVERSAL 1-CLICK HD DOWNLOADER ---
with tab2:
    st.subheader("🎬 Orbix ग्लोबल मनोरंजन प्लेयर")
    st.write("दुनिया के किसी भी डिवाइस में बिना किसी विज्ञापन या बाहरी वेबसाइट के सीधे 720p HD वीडियो डाउनलोड करें!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix वीडियो और HD लिंक्स ढूंढ रहा है..."):
                try:
                    # Fetch video metadata natively via yt-dlp json dump
                    command = f'yt-dlp "ytsearch1:{video_name}" --dump-json'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        video_data = json.loads(result.stdout)
                        video_id = video_data.get('id', '')
                        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        # Extract the best combined/progressive format url natively from youtube servers
                        # First try to find format 22 (Native 720p HD containing both audio and video)
                        hd_direct_stream_url = None
                        for fmt in video_data.get('formats', []):
                            if fmt.get('format_id') == '22' and fmt.get('url'):
                                hd_direct_stream_url = fmt['url']
                                break
                        
                        # If format 22 is missing, grab the highest available progressive format automatically
                        if not hd_direct_stream_url:
                            for fmt in video_data.get('formats', []):
                                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('url'):
                                    hd_direct_stream_url = fmt['url']
                                    if fmt.get('height', 0) >= 480:
                                        break
                        
                        st.session_state.search_result = {
                            "title": video_data.get('title', 'Video'),
                            "youtube_url": youtube_url,
                            "download_url": hd_direct_stream_url or video_data.get('url')
                        }
                        st.rerun()
                    else:
                        st.error("❌ कोई वीडियो नहीं मिला।")
                except Exception as search_err:
                    st.error(f"❌ खोजने में समस्या हुई: {str(search_err)}")

    if st.session_state.search_result:
        res = st.session_state.search_result
        st.success(f"🎯 वीडियो मिल गया: **{res['title']}**")
        
        # Native Video Playback inside Orbix App
        st.video(res['youtube_url'])
        
        st.write("---")
        st.subheader("📥 1-क्लिक डायरेक्ट यूनिवर्सल डाउनलोड")
        st.write("नीचे दिए गए लाल बटन पर क्लिक करें। कोई बाहरी विज्ञापन पेज नहीं खुलेगा, आपके क्रोम ब्राउज़र में सीधा डाउनलोड शुरू होगा:")
        
        if res['download_url']:
            # Universal Pure HTML Anchor trigger with download attribute
            # This bypasses all website blockades in India completely
            st.markdown(f'''
                <div style="margin-top: 10px;">
                    <a href="{res['download_url']}" target="_blank" download="{res['title']}.mp4">
                        <button style="background-color: #ff4b4b; color: white; padding: 16px 32px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 18px; width: 100%;">
                            🔥 1-Click में सीधे गैलरी में डाउनलोड करें
                        </button>
                    </a>
                </div>
            ''', unsafe_allow_html=True)
            st.caption("✨ **महत्वपूर्ण टिप:** बटन दबाते ही आपके ब्राउज़र में वीडियो प्लेयर पेज खुलेगा। वीडियो शुरू होते ही नीचे कोने में बने **3 डॉट्स (⋮)** पर टच करें और **Download** दबा दें। वीडियो सीधा गैलरी में आ जाएगा!")
        else:
            st.error("❌ डाउनलोड लिंक जनरेट नहीं हो सका।")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
