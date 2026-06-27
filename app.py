import streamlit as st
import requests
import os
from gtts import gTTS
import io

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

# Clear Chat Button in Sidebar
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
                try:
                    error_details = response.json().get('error', {}).get('message', 'Unknown Error')
                except:
                    error_details = response.text
                return f"❌ गूगल एरर (कोड {response.status_code}): {error_details}"
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
            except Exception as voice_err:
                st.write(f"⚠️ आवाज़ लोड करने में समस्या: {str(voice_err)}")

# --- TAB 2: STREAMING & DOWNLOAD (NEW WORK) ---
with tab2:
    st.subheader("🎬 Orbix मनोरंजन: स्ट्रीमिंग और डाउनलोडर")
    st.write("यहाँ आप किसी भी यूट्यूब वीडियो का लिंक डालकर उसे सीधे प्ले कर सकते हैं और डाउनलोडर लिंक पा सकते हैं।")
    
    # Input field for Video URL
    video_url = st.text_input("यूट्यूब वीडियो का लिंक (URL) यहाँ पेस्ट करें:", placeholder="https://www.youtube.com/watch?v=...")
    
    if video_url:
        if "youtube.com" in video_url or "youtu.be" in video_url:
            st.success("🎯 यूट्यूब लिंक मिल गया! नीचे आपका वीडियो लोड हो रहा है:")
            
            # 1. Video Search & Streaming Play
            st.video(video_url)
            
            st.write("---")
            # 2. Video Downloader Button/Links
            st.subheader("📥 वीडियो डाउनलोड करें")
            st.write("इस वीडियो को डाउनलोड करने के लिए नीचे दिए गए बटन का उपयोग करें:")
            
            # Creating a fast link to a well-known free download service
            download_helper_url = f"https://www.ssyoutube.com/watch?v={video_url.split('v=')[-1] if 'v=' in video_url else video_url.split('/')[-1]}"
            
            st.markdown(f'''
                <a href="{video_url.replace("youtube.com", "ssyoutube.com").replace("youtu.be/", "ssyoutube.com/watch?v=")}" target="_blank">
                    <button style="
                        background-color: #ff4b4b; 
                        color: white; 
                        padding: 10px 20px; 
                        border: none; 
                        border-radius: 5px; 
                        cursor: pointer; 
                        font-weight: bold;
                        font-size: 16px;">
                        📥 हाई-क्वालिटी में डाउनलोड करें (Download Video)
                    </button>
                </a>
            ''', unsafe_allow_html=True)
            st.caption("नोट: बटन दबाते ही एक नया टैब खुलेगा जहाँ से आप सीधे 720p/1080p में वीडियो सेव कर सकते हैं।")
        else:
            st.error("❌ कृपया केवल एक वैध यूट्यूब (YouTube) लिंक ही दर्ज करें।")

# --- TAB 3: EDUCATION ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

# --- TAB 4: AGRICULTURE ---
with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
