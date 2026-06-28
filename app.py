import streamlit as st
import requests
import os
from gtts import gTTS
import io
import subprocess
import json
import stat

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (ग्लोबल एडिशन)")

# --- AUTOMATIC CLOUD FFMPEG DEPLOYER FOR HD MERGING ---
@st.cache_resource
def download_ffmpeg_for_cloud():
    """यह फ़ंक्शन स्ट्रीमलिट क्लाउड सर्वर पर ऑटोमैटिक ffmpeg इंस्टॉल करता है ताकि 720p HD वीडियो मर्ज हो सके।"""
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg")
    
    if not os.path.exists(ffmpeg_path):
        os.makedirs(ffmpeg_dir, exist_ok=True)
        # Fetching pre-compiled static linux binary for cloud environment
        url = "https://github.com/probonopd/StaticBuilds/releases/download/ffmpeg/ffmpeg-git-amd64-static.tar.xz"
        try:
            with open(os.path.join(ffmpeg_dir, "ffmpeg.tar.xz"), "wb") as f:
                f.write(requests.get(url, timeout=30).content)
            # Extracting the executable binary cleanly
            subprocess.run(f"tar -xf {ffmpeg_dir}/ffmpeg.tar.xz -C {ffmpeg_dir} --strip-components=1", shell=True)
            if os.path.exists(ffmpeg_path):
                os.chmod(ffmpeg_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                return ffmpeg_path
        except:
            pass
    return "ffmpeg" if os.path.exists(ffmpeg_path) else None

# Pre-load ffmpeg silently in backend
ffmpeg_bin_path = download_ffmpeg_for_cloud()

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

# --- TAB 2: STREAMING & NATIVE 1-CLICK UNIVERSAL HD DOWNLOAD ---
with tab2:
    st.subheader("🎬 Orbix ग्लोबल मनोरंजन प्लेयर")
    st.write("बिना किसी ऐप (No VidMate Required) के दुनिया के किसी भी फोन में सीधे असली HD वीडियो डाउनलोड करें!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix वीडियो ट्रैक प्रोसेस कर रहा है..."):
                try:
                    # Clean search command to find the perfect video metadata matching criteria
                    command = f'yt-dlp "ytsearch1:{video_name}" --get-id --get-title'
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output_lines = result.stdout.strip().split('\n')
                    
                    if len(output_lines) >= 2:
                        st.session_state.search_result = {
                            "title": output_lines[0],
                            "id": output_lines[1],
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
        
        # Native Playback Video Stream
        st.video(res['youtube_url'])
        
        st.write("---")
        st.subheader("📥 इन-ऐप यूनिवर्सल HD (720p) डायरेक्ट डाउनलोडर")
        st.write("नीचे दिए गए बटन पर क्लिक करें। सर्वर बैकएंड में असली **34MB+ HD फ़ाइल** को आपके लिए प्रोसेस करके सीधा सेव कर देगा:")

        # Output filename for safety
        output_filename = "downloaded_hd_video.mp4"
        
        # Trigger actual high quality merger sequence within python backend execution
        if st.button("⚡ असली 720p HD फ़ाइल (34MB+) डाउनलोड लिंक तैयार करें", type="primary"):
            with st.spinner("🚀 वीडियो और ऑडियो मर्ज हो रहे हैं... कृपया 5 से 10 सेकंड का समय दें (प्रोसेसिंग ऑन क्लाउड)"):
                try:
                    # Cleaning previous artifacts if any
                    if os.path.exists(output_filename):
                        os.remove(output_filename)
                        
                    # Target 720p video format along with best clear audio track merged seamlessly
                    ffmpeg_arg = f"--ffmpeg-location {os.path.join(os.getcwd(), 'ffmpeg_bin')}" if ffmpeg_bin_path else ""
                    dl_command = f'yt-dlp {ffmpeg_arg} -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --merge-output-format mp4 "{res["youtube_url"]}" -o {output_filename}'
                    
                    process_res = subprocess.run(dl_command, shell=True, capture_output=True, text=True)
                    
                    if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                        with open(output_filename, "rb") as file_data:
                            video_bytes = file_data.read()
                        
                        # Real native browser trigger download button
                        st.download_button(
                            label=f"📥 यहाँ क्लिक करें - {res['title']}.mp4 डाउनलोड करें (True HD)",
                            data=video_bytes,
                            file_name=f"{res['title']}.mp4",
                            mime="video/mp4",
                            key="final_native_dl"
                        )
                        st.balloons()
                        st.success("✅ असली HD फ़ाइल तैयार है! ऊपर दिए गए बटन को दबाकर तुरंत गैलरी में सेव करें।")
                    else:
                        # Direct unblocked backup if local compile gets interrupted
                        st.markdown(f'''
                            <a href="https://9xbuddy.com/process?url={res['youtube_url']}" target="_blank">
                                <button style="background-color: #e67e22; color: white; padding: 15px; border: none; border-radius: 6px; width: 100%; font-weight: bold;">
                                    ⚠️ सर्वर बिजी है: यहाँ से 1-Click में HD डाउनलोड करें (Backup Link)
                                </button>
                            </a>
                        ''', unsafe_allow_html=True)
                except Exception as dl_error:
                    st.error(f"❌ डाउनलोड प्रोसेसिंग एरर: {str(dl_error)}")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
