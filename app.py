
import streamlit as st
import requests

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
        
        # Updated to stable v1 endpoint
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": user_query}]}]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                # यह लाइन हमें बताएगी कि गूगल को क्या दिक्कत है (जैसे: Invalid Key, Billing, or Region)
                error_details = response.json().get('error', {}).get('message', 'Unknown Error')
                return f"❌ गूगल एरर (कोड {response.status_code}): {error_details}"
        except Exception as e:
            return f"❌ तकनीकी समस्या: {str(e)}"

    query = st.text_input("Orbix से कुछ भी पूछें...", key="search_input")
    if st.button("पूछें", type="primary"):
        if query:
            with st.spinner("Orbix सोच रहा है..."):
                response_text = get_ai_response(query, api_key)
                st.write(response_text)
        else:
            st.warning("कृपया अपना सवाल लिखें।")

with tab2:
    st.subheader("🎬 मनोरंजन और स्ट्रीमिंग टूल")
    st.info("यह फीचर अगले मॉड्यूल में एक्टिव होगा।")

with tab3:
    st.subheader("📚 एडवांस ग्लोबल शिक्षा AI")
    st.info("शिक्षा और थ्योरम सॉल्विंग टूल जल्द आ रहा है।")

with tab4:
    st.subheader("🌾 कृषि टूल (Agriculture AI)")
    st.info("फसल की बीमारी पहचानने का टूल जल्द आ रहा है।")
