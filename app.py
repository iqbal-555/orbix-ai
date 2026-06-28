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
    st.session_state.search_result = None
    st.rerun()

if "search_result" not in st.session_state:
    st.session_state.search_result = None

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
                return f"❌ गूगल एरर"
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
            
# --- TAB 2: STREAMING & TRUE 1-CLICK HD DOWNLOAD ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन सर्च")
    st.write("यहाँ गाने का नाम लिखें। Orbix उसे 1-क्लिक में सीधे मोबाइल गैलरी में डाउनलोड करेगा!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix इंटरनेट पर वीडियो ढूंढ रहा है..."):
                try:
                    # Search and fetch clean download URL natively using format 18 (Standard 360p/480p combined) or highest single stream
                    command = f'yt-dlp "ytsearch1:{video_name}" --dump-json'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        video_data = json.loads(result.stdout)
                        
                        # Extracting a clean format url that won't give 403 (progressive download streams)
                        download_url = None
                        for fmt in video_data.get('formats', []):
                            # format_id 18 or 22 are perfect for direct browser downloads without 403 block
                            if fmt.get('format_id') in ['22', '18'] and fmt.get('url'):
                                download_url = fmt['url']
                                break
                        
                        if not download_url:
                            # Fallback to any working single stream link
                            for fmt in video_data.get('formats', []):
                                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('url'):
                                    download_url = fmt['url']
                                    break
                        
                        st.session_state.search_result = {
                            "title": video_data.get('title', 'Video'),
                            "id": video_data.get('id', ''),
                            "youtube_url": f"https://www.youtube.com/watch?v={video_data.get('id', '')}",
                            "direct_download_url": download_url or video_data.get('url')
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
        st.subheader("📥 1-क्लिक डायरेक्ट वीडियो डाउनलोड")
        st.write("नीचे दिए गए बटन पर क्लिक करते ही बिना किसी दूसरी वेबसाइट पर जाए वीडियो सीधे डाउनलोड होना शुरू हो जाएगा:")
        
        if res['direct_download_url']:
            # Using streamlits native container to pipe the video binary directly into the browser download manager safely
            try:
                with st.spinner("डाउनलोडर लिंक सिंक हो रहा है..."):
                    # We stream the file data using requests to avoid memory crash
                    video_file_response = requests.get(res['direct_download_url'], stream=True)
                    video_bytes = video_file_response.content
                
                st.download_button(
                    label="🔥 सीधे अपने मोबाइल में डाउनलोड करें (Instant Save)",
                    data=video_bytes,
                    file_name=f"{res['title']}.mp4",
                    mime="video/mp4",
                    type="primary"
                )
                st.caption("✨ नोट: इस बटन को दबाते ही वीडियो सीधा आपके नोटिफिकेशन बार में डाउनलोड होने लगेगा। कोई विज्ञापन या रिडायरेक्ट नहीं!")
            except Exception as dl_bt_err:
                st.error("⚠️ डायरेक्ट इन-ऐप सर्वर डाउनलोड उपलब्ध नहीं है, कृपया अल्टरनेटिव लिंक यूज़ करें।")
                st.markdown(f'<a href="{res["direct_download_url"]}" target="_blank"><button style="background-color:#e74c3c;color:white;padding:12px;border:none;border-radius:5px;width:100%;font-weight:bold;">🔗 अल्टरनेटिव डायरेक्ट लिंक से डाउनलोड करें</button></a>', unsafe_allow_html=True)
        else:
            st.error("❌ डाउनलोड लिंक जेनरेट नहीं हो सका।")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
