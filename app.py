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

# Sidebar for API Key Settings
st.sidebar.title("⚙️ Orbix कंट्रोल पैनल")
api_key = st.sidebar.text_input("Gemini API Key दर्ज करें", type="password", help="अपना फ्री API की यहाँ डालें")
language = st.sidebar.selectbox("🌐 भाषा चुनें (Select Language)", ["Hindi", "English", "Urdu", "Global"])

# Chat Memory System initializing
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.sidebar.button("🧹 चैट इतिहास साफ़ करें"):
    st.session_state.chat_history = []
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
    .ai-msg { background-color: #f1f8e9; padding: 10px; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)
    
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

    def get_ai_response_with_memory(user_query, key, history):
        if not key:
            return "❌ कृपया साइडबार (Sidebar) में अपनी Gemini API Key डालें। यह बिल्कुल फ्री है!"
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
                return f"❌ गूगल एरर (कोड {response.status_code})"
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    query = st.text_input("Orbix से कुछ भी पूछें...", key="search_input_mem")
    if st.button("पूछें", type="primary", key="send_btn"):
        if query:
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_ai_response_with_memory(query, api_key, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "user", "text": query})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                st.rerun()
        else:
            st.warning("कृपया अपना सवाल लिखें।")
            
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

# --- TAB 2: STREAMING & DIRECT HD DOWNLOAD ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन सर्च")
    st.write("यहाँ किसी भी गाने या वीडियो का नाम लिखें। Orbix उसे 720p/Best क्वालिटी में लाएगा!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary"):
        if video_name:
            with st.spinner("Orbix इंटरनेट से HD डायरेक्ट डाउनलोड लिंक निकाल रहा है..."):
                try:
                    # Requesting yt-dlp to look for best combined formats or 720p directly
                    command = f'yt-dlp "ytsearch1:{video_name}" --dump-json'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        video_data = json.loads(result.stdout)
                        video_title = video_data.get('title', 'Video')
                        video_id = video_data.get('id', '')
                        actual_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        st.success(f"🎯 वीडियो मिल गया: **{video_title}**")
                        
                        # Play Video in App
                        st.video(actual_url)
                        
                        st.write("---")
                        st.subheader("📥 डायरेक्ट HD वीडियो डाउनलोड लिंक")
                        st.write("नीचे दिए गए बटन पर क्लिक करें। प्लेयर खुलने पर कोने में 3 डॉट्स (⋮) दबाकर Download करें:")
                        
                        # Advanced filtering for 720p or highest progressive format available
                        hd_download_url = None
                        best_fallback_url = None
                        
                        for fmt in video_data.get('formats', []):
                            # Progressive download formats (have both video and audio)
                            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('url'):
                                height = fmt.get('height', 0)
                                if height == 720:
                                    hd_download_url = fmt['url']
                                    break
                                elif height > 360:
                                    best_fallback_url = fmt['url']
                        
                        # If exact 720p with audio isn't separated, take the best single URL format
                        final_link = hd_download_url or best_fallback_url or video_data.get('url')
                        
                        if final_link:
                            st.markdown(f'''
                                <a href="{final_link}" target="_blank">
                                    <button style="background-color: #ff4b4b; color: white; padding: 14px 28px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; width: 100%;">
                                        🔥 HD क्वालिटी में डाउनलोड करें (Download 720p/Best)
                                    </button>
                                </a>
                            ''', unsafe_allow_html=True)
                        else:
                            st.error("❌ डायरेक्ट डाउनलोड लिंक जनरेट नहीं हो सका।")
                    else:
                        st.error("❌ कोई वीडियो नहीं मिला।")
                except Exception as search_err:
                    st.error(f"❌ खोजने में समस्या हुई: {str(search_err)}")
        else:
            st.warning("कृपया किसी गाने या वीडियो का नाम दर्ज करें।")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
