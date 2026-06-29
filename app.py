import streamlit as st
import requests
import os
from gtts import gTTS
import io
import base64
import uuid
from supabase import create_client, Client

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट (एडवांस चैट सेशन एडिशन)")

# --- SECURE DATABASE & API CONFIGURATION ---
if "GEMINI_API_KEY" in st.secrets:
    DEFAULT_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    DEFAULT_API_KEY = ""

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as init_err:
        st.error(f"❌ डेटाबेस कनेक्शन एरर: {str(init_err)}")

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "recent_chats_list" not in st.session_state:
    st.session_state.recent_chats_list = {}

# --- SIDEBAR CONTROL PANEL (GEMINI LOOK) ---
st.sidebar.title("⚙️ Orbix कंट्रोल पैनल")

if st.session_state.logged_in:
    st.sidebar.success(f"👤 {st.session_state.user_email}")
    
    # 📝 NEW CHAT BUTTON (JUST LIKE IMAGE)
    if st.sidebar.button("📝 New chat", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.toast("✨ नया चैट सेशन शुरू हुआ!")
        st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("🕒 Recent Chats")
    
    # Load unique chat sessions from Supabase for this user
    if supabase:
        try:
            # Fetching unique sessions sorted by latest updates
            db_res = supabase.table("chats").select("chat_id, user_msg").eq("user_email", st.session_state.user_email).order("created_at", ascending=True).execute()
            
            # Map first message of each unique chat_id as its title
            sessions = {}
            for row in db_res.data:
                c_id = row.get("chat_id")
                msg = row.get("user_msg", "Purani Chat")
                if c_id and c_id not in sessions:
                    # Clean title if it's a media attachment
                    title = msg if not msg.startswith("📎") else msg.split("] ", 1)[-1]
                    sessions[c_id] = title[:28] + "..." if len(title) > 28 else title
            
            st.session_state.recent_chats_list = sessions
        except:
            pass

    # Render Recent Chat Buttons dynamically in the sidebar
    if st.session_state.recent_chats_list:
        for s_id, s_title in st.session_state.recent_chats_list.items():
            # Highlight current active chat
            is_active = "🎯 " if s_id == st.session_state.current_chat_id else "💬 "
            if st.sidebar.button(f"{is_active}{s_title}", key=f"session_{s_id}", use_container_width=True):
                st.session_state.current_chat_id = s_id
                # Fetch messages for selected session
                try:
                    history_res = supabase.table("chats").select("*").eq("chat_id", s_id).order("created_at", ascending=True).execute()
                    st.session_state.chat_history = []
                    for row in history_res.data:
                        st.session_state.chat_history.append({"role": "user", "text": row["user_msg"]})
                        st.session_state.chat_history.append({"role": "model", "text": row["ai_reply"]})
                    st.rerun()
                except:
                    st.error("❌ चैट लोड करने में दिक्कत हुई।")
    else:
        st.sidebar.caption("कोई पुरानी चैट नहीं मिली।")

    st.sidebar.markdown("---")
    language = st.sidebar.selectbox("🌐 भाषा (Language)", ["Hindi", "English", "Urdu", "Global"])
    
    if st.sidebar.button("Log out 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.chat_history = []
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()

# --- BACKUP PASSWORD RESET CHECK ---
is_recovery = False
query_params = st.query_params
if "type" in query_params and query_params["type"] == "recovery":
    is_recovery = True

if not st.session_state.logged_in and not is_recovery:
    if st.sidebar.checkbox("🔑 Force Reset Screen"):
        is_recovery = True

# --- APP INTERFACE ROUTING ---
if is_recovery:
    st.subheader("🔒 नया पासवर्ड सेट करें (Reset Password)")
    new_password = st.text_input("नया मजबूत पासवर्ड (New Password)", type="password")
    confirm_new_password = st.text_input("पासवर्ड दोबारा डालें", type="password")
    
    if st.button("पासवर्ड अपडेट करें (Update Password) 💾", type="primary"):
        if len(new_password) < 6:
            st.warning("⚠️ पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।")
        elif new_password != confirm_new_password:
            st.error("❌ पासवर्ड मैच नहीं हुए।")
        else:
            try:
                supabase.auth.update_user({"password": new_password})
                st.success("🎉 पासवर्ड बदल गया! अब लॉगिन करें।")
                st.query_params.clear()
            except Exception as e:
                st.error(f"❌ विफल: {str(e)}")
                    
elif not st.session_state.logged_in:
    st.subheader("🔒 Orbix AI सुरक्षित प्रवेश द्वार")
    login_tab, signup_tab, reset_tab = st.tabs(["🔐 Sign In", "📝 Sign Up", "🔑 Forgot Password"])
    
    with login_tab:
        login_email = st.text_input("ईमेल आईडी (Email)", key="l_email")
        login_password = st.text_input("पासवर्ड (Password)", type="password", key="l_pass")
        if st.button("प्रवेश करें (Login) ➔", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.logged_in = True
                st.session_state.user_email = login_email
                st.rerun()
            except:
                st.error("❌ लॉगिन विफल! विवरण जांचें।")
                        
    with signup_tab:
        reg_email = st.text_input("ईमेल आईडी डालें", key="r_email")
        reg_password = st.text_input("पासवर्ड चुनें", type="password", key="r_pass")
        if st.button("अकाउंट बनाएं ✨"):
            try:
                res = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                st.success("🎉 अकाउंट बन गया! अब लॉगिन करें।")
            except Exception as e:
                st.error(f"❌ विफल: {str(e)}")

    with reset_tab:
        reset_email = st.text_input("रजिस्टर्ड ईमेल आईडी", key="reset_em")
        if st.button("रीसेट लिंक भेजें ✉️"):
            try:
                supabase.auth.reset_password_for_email(reset_email)
                st.success("🎯 लिंक आपके ईमेल पर भेज दिया गया है!")
            except Exception as e:
                st.error(f"❌ विफल: {str(e)}")

else:
    # --- MAIN CHAT APP REGION ---
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Orbix Chat", "🎬 मनोरंजन", "📚 शिक्षा", "🌾 कृषि"])

    with tab1:
        st.subheader("💬 Orbix AI से सीधी बातचीत")
        
        st.markdown("""
            <style>
            .user-msg { background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; color: #0d47a1; }
            .ai-msg { background-color: #f1f8e9; padding: 10px; border-radius: 10px; margin: 5px 0; color: #1b5e20; }
            </style>
        """, unsafe_allow_html=True)

        # Render current conversation
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="user-msg">🧑 <b>आप:</b> {chat["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg">🚀 <b>Orbix:</b> {chat["text"]}</div>', unsafe_allow_html=True)

        def get_gemini_response(user_query, key, history):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            contents = []
            for chat in history:
                contents.append({"role": "user" if chat["role"] == "user" else "model", "parts": [{"text": chat["text"]}]})
            contents.append({"role": "user", "parts": [{"text": user_query}]})
            try:
                res = requests.post(url, json={"contents": contents})
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            except:
                return "❌ गूगल रिस्पॉन्स एरर।"

        chat_media = st.file_uploader("➕ फोटो या वीडियो जोड़ें", type=["jpg", "jpeg", "png", "mp4"])
        
        if query := st.chat_input("Ask Orbix anything..."):
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_gemini_response(query, DEFAULT_API_KEY, st.session_state.chat_history)
                display_text = query if not chat_media else f"📎 [{chat_media.name}] {query}"
                
                st.session_state.chat_history.append({"role": "user", "text": display_text})
                st.session_state.chat_history.append({"role": "model", "text": response_text})
                
                # Auto-save inside specific chat session id
                if supabase:
                    try:
                        supabase.table("chats").insert({
                            "user_email": st.session_state.user_email,
                            "chat_id": st.session_state.current_chat_id,
                            "user_msg": display_text,
                            "ai_reply": response_text
                        }).execute()
                    except:
                        pass
                st.rerun()

        # Audio Output for Latest message
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

    # --- OTHER TABS ---
    with tab2:
        st.subheader("🎬 Orbix स्मार्ट मनोरंजन प्लेयर")
        video_name = st.text_input("📝 वीडियो का नाम लिखें:")
        if st.button("वीडियो ढूंढें 🔍") and video_name:
            with st.spinner("ढूंढ रहा है..."):
                try:
                    import subprocess
                    result = subprocess.run(f'yt-dlp "ytsearch1:{video_name}" --get-id --get-title', shell=True, capture_output=True, text=True)
                    output_lines = result.stdout.strip().split('\n')
                    if len(output_lines) >= 2:
                        st.write(f"🎯 **{output_lines[0]}**")
                        st.video(f"https://www.youtube.com/watch?v={output_lines[1]}")
                except:
                    st.error("❌ खोजने में समस्या हुई।")

    with tab3: st.info("जल्द आ रहा है।")
    with tab4: st.info("जल्द आ रहा है।")
