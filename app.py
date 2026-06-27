
import streamlit as st
import requests
import urllib.parse

st.set_page_config(page_title="Orbix AI", page_icon="🚀", layout="wide")

st.title("🚀 ORBIX AI")
st.caption("द नेक्स्ट-जेन बिलियन डॉलर एआई असिस्टेंट")

# Sidebar for API Key Settings
st.sidebar.title("⚙️ Orbix कंट्रोल पैनल")
api_key = st.sidebar.text_input("Gemini API Key दर्ज करें", type="password", help="अपना फ्री API की यहाँ डालें")

language = st.sidebar.selectbox("🌐 भाषा चुनें (Select Language)", ["Hindi", "English", "Urdu", "Global"])

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Orbix Chat (AI दिमाग)", 
    "🎬 मनोरंजन (Streaming & Download)", 
    "📚 शिक्षा (1st to M.Sc)", 
    "🌾 कृषि टूल (Agriculture AI)"
])

with tab1:
    st.subheader("💬 Orbix AI से सीधी बातचीत")
    
    def get_ai_response(user_query, key):
        if not key:
            return "❌ कृपया साइडबार (Sidebar) में अपनी Gemini API Key डालें। यह बिल्कुल फ्री है!"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": user_query}]}]
        }
        
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

    query = st.text_input("Orbix से कुछ भी पूछें...", key="search_input")
    if st.button("पूछें", type="primary"):
        if query:
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_ai_response(query, api_key)
                st.write(response_text)
                
                # --- Voice Output Feature ---
                if not response_text.startswith("❌"):
                    # क्लीन टेक्स्ट तैयार करना (ताकि बोलने में कोई दिक्कत न हो)
                    clean_text = response_text.replace('*', '').replace('#', '')
                    encoded_text = urllib.parse.quote(clean_text)
                    
                    # भाषा के हिसाब से आवाज़ सेट करना
                    tts_lang = "hi" if language == "Hindi" else "en"
                    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={tts_lang}&client=tw-ob&q={encoded_text}"
                    
                    st.write("🔊 **जवाब सुनें:**")
                    st.audio(tts_url, format="audio/mp3")
        else:
            st.warning("कृपया अपना सवाल लिखें।")

with tab2:
    st.subheader("🎬 मनोरंजन और streaming टूल")
    st.info("यह फीचर अगले मॉड्यूल में एक्टिव होगा।")

with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
