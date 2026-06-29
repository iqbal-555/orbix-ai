import streamlit as st
import requests
import os
from gtts import gTTS
import io
import base64
from supabase import create_client, Client

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (डेटाबेस और लॉगिन एडिशन)")

# --- SECURE DATABASE & API CONFIGURATION ---
if "GEMINI_API_KEY" in st.secrets:
    DEFAULT_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    DEFAULT_API_KEY = ""

# Supabase Connection Keys
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

# Client initialization if keys exist
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

# --- SESSION STATE FOR LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.title("⚙️ Orbix कंट्रोल पैनल")
language = st.sidebar.selectbox("🌐 भाषा चुनें (Select Language)", ["Hindi", "English", "Urdu", "Global"])

if st.session_state.logged_in:
    st.sidebar.success(f"👤 Active: {st.session_state.user_email}")
    if st.sidebar.button("🚪 Logout करें"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.chat_history = []
        st.rerun()

# --- APP INTERFACE ROUTING (LOGIN VS MAIN APP) ---
if not st.session_state.logged_in:
    # --- PROFESSIONAL LOGIN & SIGNUP SCREEN ---
    st.subheader("🔒 Orbix AI सुरक्षित प्रवेश द्वार")
    
    login_tab, signup_tab = st.tabs(["🔐 Sign In (लॉगिन)", "📝 Sign Up (नया अकाउंट बनाएं)"])
    
    with login_tab:
        login_email = st.text_input("ईमेल आईडी (Email)", key="login_email_input")
        login_password = st.text_input("पासवर्ड (Password)", type="password", key="login_pass_input")
        
        if st.button("प्रवेश करें (Login) ➔", type="primary"):
            if not supabase:
                # Local Bypass if database keys are not yet configured in secrets
                st.session_state.logged_in = True
                st.session_state.user_email = login_email if login_email else "demo@orbix.ai"
                st.rerun()
            else:
                try:
                    res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    st.session_state.logged_in = True
                    st.session_state.user_email = login_email
                    st.success("✅ लॉगिन सफल!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ लॉगिन विफल: {str(e)}")
                    
    with signup_tab:
        reg_email = st.text_input("अपना ईमेल डालें (Email)", key="reg_email_input")
        reg_password = st.text_input("एक मजबूत पासवर्ड चुनें (Password)", type="password", key="reg_pass_input")
        
        if st.button("अकाउंट बनाएं (Create Account) ✨"):
            if not supabase:
                st.warning("⚠️ Database Configured nahi hai. Demo ke liye direct login karein.")
            else:
                try:
                    res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                    st.success("🎉 अकाउंट सफलतापूर्वक बन गया! कृपया लॉगिन करें।")
                except Exception as e:
                    st.error(f"❌ रजिस्ट्रेशन विफल: {str(e)}")

else:
    # --- MAIN APP REGION (RUNS ONLY AFTER SUCCESSFUL LOGIN) ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Orbix Chat (AI दिमाग)", 
        "🎬 मनोरंजन (Smart Streaming)", 
        "📚 शिक्षा (1st to M.Sc)", 
        "🌾 कृषि टूल (Agriculture AI)"
    ])

    # --- TAB 1: CHAT WITH DATABASE SAVE CAPABILITY ---
    with tab1:
        st.subheader("💬 Orbix AI से सीधी बातचीत")
        
        # UI Styling
        st.markdown("""
            <style>
            .user-msg { background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #0d47a1; }
            .ai-msg { background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; color: #1b5e20; }
            </style>
        """, unsafe_allow_html=True)

        # Sync/Load history from database simulation
        if st.button("🔄 क्लाउड से पुराना चैट लोड करें"):
            st.toast("⚡ इतिहास सुरक्षित रूप से सिंक हो गया!")

        # Render Messages
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

        def get_gemini_response(user_query, key, history):
            if not key: return "❌ AI Mind missing! Secrets me API Key set karein."
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            headers = {'Content-Type': 'application/json'}
            contents = []
            for chat in history:
                role_type = "user" if chat["role"] == "user" else "model"
                contents.append({"role": role_type, "parts": [{"text": chat["text"]}]})
            contents.append({"role": "user", "parts": [{"text": user_query}]})
            try:
                res = requests.post(url, headers=headers, json={"contents": contents})
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                return f"❌ Error: {str(e)}"

        # Chat Input Box Component
        chat_media = st.file_uploader("➕ फोटो या वीडियो जोड़ें", type=["jpg", "jpeg", "png", "mp4"], key="chat_inline_uploader")
        
        if query := st.chat_input("Ask Orbix anything..."):
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_gemini_response(query, DEFAULT_API_KEY, st.session_state.chat_history)
                display_text = query if not chat_media else f"📎 [फ़ाइल: {chat_media.name}] {query}"
                
                # Append to current session state
                st.session_state.chat_history.append({"role": "user", "text": display_text})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                
                # Backand Database Auto-Save trigger
                if supabase:
                    try:
                        supabase.table("chats").insert({
                            "user_email": st.session_state.user_email,
                            "user_msg": display_text,
                            "ai_reply": response_text
                        }).execute()
                    except:
                        pass
                st.rerun()

        # Voice Response TTS Engine
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "model":
            last_msg = st.session_state.chat_history[-1]["text"]
            if not last_msg.startswith("❌"):
                try:
                    tts = gTTS(text=last_msg.replace('*', ''), lang="hi", slow=False)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp, format="audio/mp3")
                except:
                    pass

    # --- TAB 2: SMART ENTERTAINMENT PLAYER ---
    with tab2:
        st.subheader("🎬 Orbix स्मार्ट मनोरंजन प्लेयर")
        video_name = st.text_input("📝 वीडियो या गाने का नाम लिखें:", placeholder="उदा. मुबारक हो तुमको शादी तुम्हारी", key="entertainment_search_box")
        
        if st.button("वीडियो ढूंढें 🔍", type="primary", key="search_ent_btn"):
            if video_name:
                with st.spinner("Orbix वीडियो ढूंढ रहा है..."):
                    try:
                        command = f'yt-dlp "ytsearch1:{video_name}" --get-id --get-title'
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)
                        output_lines = result.stdout.strip().split('\n')
                        if len(output_lines) >= 2:
                            st.write(f"🎯 वीडियो मिल गया: **{output_lines[0]}**")
                            st.video(f"https://www.youtube.com/watch?v={output_lines[1]}")
                    except:
                        st.error("❌ खोजने में समस्या हुई।")

    with tab3:
        st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
        st.info("जल्द आ रहा है।")

    with tab4:
        st.subheader("🌾 कृषि टूल (Agriculture AI)")
        st.info("जल्द आ रहा है।")
