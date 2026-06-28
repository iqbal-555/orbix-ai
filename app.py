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

# Persistence for entertainment tab search
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

# --- TAB 2: STREAMING & IN-APP SERVER HD DOWNLOAD (NO MORE 403 ERRORS) ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन सर्च")
    st.write("यहाँ किसी भी गाने या वीडियो का नाम लिखें। Orbix उसे सीधे ऐप के अंदर डाउनलोड के लिए तैयार करेगा!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix इंटरनेट पर वीडियो ढूंढ रहा है..."):
                try:
                    command = f'yt-dlp "ytsearch1:{video_name}" --dump-json'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        video_data = json.loads(result.stdout)
                        st.session_state.search_result = {
                            "title": video_data.get('title', 'Video'),
                            "id": video_data.get('id', ''),
                            "url": f"https://www.youtube.com/watch?v={video_data.get('id', '')}"
                        }
                        st.rerun()
                    else:
                        st.error("❌ कोई वीडियो नहीं मिला। कृपया नाम बदलें।")
                except Exception as search_err:
                    st.error(f"❌ खोजने में समस्या हुई: {str(search_err)}")
        else:
            st.warning("कृपया किसी गाने या वीडियो का नाम दर्ज करें।")

    # Display result and handling Server-Side HD download
    if st.session_state.search_result:
        res = st.session_state.search_result
        st.success(f"🎯 वीडियो मिल गया: **{res['title']}**")
        
        # Play Video in App
        st.video(res['url'])
        
        st.write("---")
        st.subheader("📥 डायरेक्ट HD (720p) डाउनलोड कंट्रोल")
        
        # Define secure temporary path on Streamlit Server
        tmp_file_path = f"/tmp/{res['id']}.mp4"
        
        # Step 1: Check if file is downloaded on server, if not show button to prepare it
        if not os.path.exists(tmp_file_path):
            st.info("💡 इस वीडियो को HD 720p में डाउनलोड करने के लिए नीचे दिए गए बटन पर क्लिक करके फ़ाइल तैयार करें:")
            if st.button("⚡ HD 720p फ़ाइल तैयार करें (Prepare High Quality)", type="secondary"):
                with st.spinner("Orbix फ़ाइल को 720p HD में कन्वर्ट कर रहा है, कृपया 5-10 सेकंड रुकें..."):
                    # Command to download max 720p merged video+audio natively on server
                    dl_cmd = f'yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --merge-output-format mp4 -o "{tmp_file_path}" "{res["url"]}"'
                    subprocess.run(dl_cmd, shell=True)
                st.rerun()
        else:
            # Step 2: Once downloaded on server, provide the clean binary Streamlit download button
            st.success("✨ HD फ़ाइल डाउनलोड के लिए तैयार है!")
            with open(tmp_file_path, "rb") as file:
                st.download_button(
                    label="🔥 सीधे अपने मोबाइल गैलरी में सेव करें (Save to Mobile Gallery)",
                    data=file,
                    file_name=f"{res['title']}.mp4",
                    mime="video/mp4",
                    type="primary"
                )
            st.caption("नोट: इस बटन को दबाते ही बिना किसी एरर या विज्ञापन के वीडियो सीधा आपकी गैलरी में डाउनलोड हो जाएगा।")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
