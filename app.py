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
# Streamlit Secrets या environment variables से की (Key) उठाएगा
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

# --- TAB 2: STREAMING & TRUE HD (720p) VIDEO DOWNLOAD ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन सर्च")
    st.write("यहाँ गाने का नाम लिखें। Orbix सीधे असली HD 720p वीडियो फ़ाइल तैयार करेगा!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix इंटरनेट पर वीडियो ढूंढ रहा है..."):
                try:
                    command = f'yt-dlp "ytsearch1:{video_name}" --get-id --get-title'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output_lines = result.stdout.strip().split('\n')
                    
                    if len(output_lines) >= 2:
                        st.session_state.search_result = {
                            "title": output_lines[0],
                            "id": output_lines[1],
                            "url": f"https://www.youtube.com/watch?v={output_lines[1]}"
                        }
                        st.rerun()
                    else:
                        st.error("❌ कोई वीडियो नहीं मिला।")
                except Exception as search_err:
                    st.error(f"❌ खोजने में समस्या हुई: {str(search_err)}")

    if st.session_state.search_result:
        res = st.session_state.search_result
        st.success(f"🎯 वीडियो मिल गया: **{res['title']}**")
        
        # Play Video Stream
        st.video(res['url'])
        
        st.write("---")
        st.subheader("📥 1-क्लिक डायरेक्ट HD 720p वीडियो डाउनलोड")
        
        # Define cloud server path
        local_video_path = f"/tmp/{res['id']}.mp4"
        
        # If video is not processed yet on cloud backend
        if not os.path.exists(local_video_path):
            st.info("🔄 इस वीडियो को असली HD 720p वीडियो फ़ॉर्मेट में डाउनलोड करने के लिए नीचे बटन दबाएं:")
            if st.button("🎬 HD 720p वीडियो फ़ाइल तैयार करें", type="secondary"):
                with st.spinner("Orbix क्लाउड सर्वर पर असली वीडियो डाउनलोड और मर्ज कर रहा है... इसमें 15-20 सेकंड लग सकते हैं।"):
                    # This forces yt-dlp to download and stitch real 720p video + audio together into a pure MP4 file
                    build_cmd = f'yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --merge-output-format mp4 -o "{local_video_path}" "{res["url"]}"'
                    subprocess.run(build_cmd, shell=True)
                st.rerun()
        else:
            # When ready, open the file binary stream natively to trigger proper browser download manager
            st.success("✨ असली HD 720p वीडियो डाउनलोड के लिए बिल्कुल तैयार है!")
            try:
                with open(local_video_path, "rb") as f:
                    st.download_button(
                        label="🔥 सीधे गैलरी में असली वीडियो सेव करें (Save HD Video)",
                        data=f,
                        file_name=f"{res['title']}.mp4",
                        mime="video/mp4",
                        type="primary"
                    )
                st.caption("नोट: इस बटन को दबाते ही असली HD वीडियो सीधे आपके मोबाइल स्टोरेज में आ जाएगा।")
            except Exception as io_err:
                st.error(" can't load file.")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
