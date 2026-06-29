    # --- ADVANCED FIXED BOTTOM CHATGPT/GEMINI INPUT BAR ---
    components.html("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #ffffff; padding: 10px 15px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center; gap: 10px; z-index: 99999; font-family: sans-serif;">
            <div style="display: flex; align-items: center; width: 100%; max-width: 700px; background: #ffffff; border: 1px solid #dadce0; border-radius: 24px; padding: 4px 12px; gap: 8px;">
                <!-- प्लस बटन -->
                <button id="plus_btn" style="background: none; border: none; font-size: 24px; color: #1a73e8; cursor: pointer; padding: 5px; display: flex; align-items: center; justify-content: center;">+</button>
                
                <!-- इनपुट फील्ड -->
                <input id="chat_input" type="text" placeholder="Ask Orbix..." style="flex-grow: 1; border: none; padding: 10px 5px; font-size: 16px; outline: none; background: transparent;" />
                
                <!-- माइक बटन -->
                <button id="mic_btn" style="background: none; border: none; font-size: 20px; color: #5f6368; cursor: pointer; padding: 5px; display: flex; align-items: center; justify-content: center;">🎤</button>
            </div>
            
            <!-- सेंड बटन (बॉक्स के बाहर, बिल्कुल ChatGPT की तरह) -->
            <button id="send_btn" style="background: #1a73e8; border: none; color: white; min-width: 44px; height: 44px; border-radius: 50%; font-weight: bold; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center;">➔</button>
        </div>
        
        <script>
            const inputField = document.getElementById('chat_input');
            const sendBtn = document.getElementById('send_btn');
            const micBtn = document.getElementById('mic_btn');
            const plusBtn = document.getElementById('plus_btn');

            // 1. Native Real-time Speech Recognition Protocol
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.lang = 'hi-IN'; // Default Hindi support
                recognition.interimResults = false;

                micBtn.onclick = function() {
                    recognition.start();
                    micBtn.style.color = "#ea4335"; // Turns red when active
                    inputField.placeholder = "🔊 Sun raha hoon, boliye...";
                };

                recognition.onresult = function(event) {
                    const text = event.results[0][0].transcript;
                    inputField.value = text;
                    micBtn.style.color = "#5f6368";
                    inputField.placeholder = "Ask Orbix...";
                };

                recognition.onerror = function() {
                    micBtn.style.color = "#5f6368";
                    inputField.placeholder = "Mic Error, try again...";
                };
            }

            // Plus trigger placeholder action
            plusBtn.onclick = function() {
                alert("📎 Gallery feature coming soon in mobile wrapper app!");
            };

            // 2. Transmit message safely to Streamlit processing pipeline
            function submitMessage() {
                const text = inputField.value.trim();
                if(text) {
                    // Inject text directly into URL query parameters to force safe fast processing
                    window.parent.location.search = "?msg=" + encodeURIComponent(text);
                }
            }

            sendBtn.onclick = submitMessage;
            inputField.addEventListener("keypress", function(e) {
                if (e.key === "Enter") { submitMessage(); }
            });
        </script>
    """, height=80)
