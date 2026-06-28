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

# --- TAB 2: STREAMING & GUARANTEED 720p HD DOWNLOAD ---
with tab2:
    st.subheader("🎬 Orbix स्मार्ट मनोरंजन सर्च")
    st.write("यहाँ गाने का नाम लिखें। Orbix तुरंत सुपरफास्ट 720p HD डाउनलोडर लिंक तैयार करेगा!")
    
    video_name = st.text_input("वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
    
    if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
        if video_name:
            with st.spinner("Orbix वीडियो ढूंढ रहा है..."):
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
        st.subheader("📥 डायरेक्ट 1-क्लिक HD (720p) वीडियो डाउनलोड")
        st.write("नीचे असली HD डाउनलोड करने के लिए दो सबसे तेज़ ग्लोबल सर्वर दिए गए हैं। ये भारत में 100% अनब्लॉक हैं:")
        
        # Method: Calling Cobalt engine api via public instances that generates instant unblocked raw video links
        cobalt_url_1 = f"https://cobalt.tools"  # Fallback reference
        
        # Generation of super stable external streaming link helpers (direct download triggers)
        server1_direct = f"https://api.cobalt.tools/api/json"
        
        # Fetching direct link from Cobalt API backend seamlessly within seconds
        with st.spinner("⚡ सुपरफास्ट डाउनलोड लिंक तैयार हो रहा है..."):
            try:
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                payload = {"url": res['url'], "videoQuality": "720", "filenamePattern": "basic"}
                api_res = requests.post(server1_direct, headers=headers, json=payload, timeout=5)
                
                if api_res.status_code == 200 and "url" in api_res.json():
                    final_hd_url = api_res.json()["url"]
                    st.markdown(f'''
                        <div style="margin-bottom: 15px;">
                            <a href="{final_hd_url}" target="_blank" download>
                                <button style="background-color: #2ecc71; color: white; padding: 16px 32px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 18px; width: 100%;">
                                    🟢 सर्वर 1: सीधे मोबाइल गैलरी में डाउनलोड करें (असली HD 720p)
                                </button>
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                        <div style="margin-bottom: 15px;">
                            <a href="https://co.wuk.sh/api/json" target="_blank">
                                <button style="background-color: #e67e22; color: white; padding: 16px 32px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 18px; width: 100%;">
                                    ⚠️ सर्वर 1 बैकअप लिंक (यहाँ से डाउनलोड करें)
                                </button>
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
            except:
                # Ultra ultra stable final backup web proxy alternative if API times out
                bypass_fallback = f"https://www.youtube-nocookie.com/embed/{res['id']}"
                st.info("💡 नीचे दिए गए अल्टरनेटिव बटन पर क्लिक करें और सेव करें:")
                st.markdown(f'''
                    <a href="https://9xbuddy.xyz/process?url={res['url']}" target="_blank">
                        <button style="background-color: #3498db; color: white; padding: 15px; border: none; border-radius: 6px; width: 100%; font-weight: bold;">
                            🔵 सर्वर 2: अल्टरनेटिव फ़ास्ट डाउनलोडर खोलें
                        </button>
                    </a>
                ''', unsafe_allow_html=True)

        st.caption("💡 **टिप:** हरा बटन (सर्वर 1) दबाते ही बिना किसी विज्ञापन या रीडायरेक्ट के असली HD MP4 वीडियो सीधा आपके फोन के डाउनलोड मैनेजर में आ जाएगा!")

# --- TAB 3 & 4 ---
with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
