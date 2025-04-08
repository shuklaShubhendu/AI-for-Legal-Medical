import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Please set the OPENAI_API_KEY in your Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Title and Description
st.set_page_config(page_title="Medical-Legal Assistant")
st.title("⚖️ Medical-Legal Assistant for Doctors in India")

st.markdown("""
This chatbot offers **informational legal guidance** for doctors in India.  
Upload legal documents (e.g., consent forms, notices), and get insights backed by Indian laws.  
📌 *Disclaimer: This is not legal advice. Always consult a qualified professional.*
""")

# Sidebar: Key Laws
with st.sidebar:
    st.header("📘 Indian Medical Law Summary")
    st.markdown("""
    - **Indian Medical Council Act, 1956**: Ethics & standards (MCI Regulations, 2002).
    - **Consumer Protection Act, 2019**: Handles negligence, services.
    - **Clinical Establishments Act, 2010**: Consent, record-keeping.
    - **NDPS Act, 1985**: Regulates narcotics.
    - **IT Act, 2000**: Ensures patient data privacy.
    - **Cases**:  
      - *Samira Kohli (2008)* – Consent  
      - *Jacob Mathew (2005)* – Medical negligence  
    """)

# Disclaimer checkbox
if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.warning("Please accept the disclaimer to proceed.")
    if st.checkbox("✅ I understand this is not legal advice."):
        st.session_state.disclaimer_accepted = True

# Chat history initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
if st.session_state.disclaimer_accepted:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # File upload
    uploaded_file = st.file_uploader("📄 Upload a legal/medical file (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
    file_id = None

    if uploaded_file:
        try:
            with st.spinner("🔁 Uploading file to OpenAI..."):
                file_response = client.files.create(
                    file=uploaded_file,
                    purpose="user_data"
                )
                file_id = file_response.id
                st.success(f"Uploaded `{uploaded_file.name}` successfully!")
        except Exception as e:
            st.error(f"File upload failed: {str(e)}")

    # User input
    user_input = st.chat_input("💬 Ask a medical-legal question...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("🧠 Thinking..."):
            try:
                messages = [
                    {
                        "role": "system",
                        "content": """
You are a legal assistant for Indian doctors. Your task is to explain legal requirements, potential liabilities, and provide guidance based on:
- Indian Medical Council Act, 1956
- Consumer Protection Act, 2019
- Clinical Establishments Act, 2010
- NDPS Act, 1985
- IT Act, 2000
Cite landmark judgments such as:
- Samira Kohli vs. Dr. Prabha Manchanda (2008)
- Jacob Mathew vs. State of Punjab (2005)
- V. Shantha vs. Indian Medical Association (1995)

When documents are uploaded, assess compliance and give actionable steps. Emphasize this is informational only, not legal advice.
                        """
                    }
                ] + st.session_state.chat_history

                if file_id:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "file", "file": {"file_id": file_id}},
                            {"type": "text", "text": user_input}
                        ]
                    })
                else:
                    messages.append({"role": "user", "content": user_input})

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )

                bot_reply = response.choices[0].message.content.strip()

                with st.chat_message("assistant"):
                    st.markdown(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Save chat to JSON
    if st.button("💾 Save Chat"):
        chat_data = {
            "timestamp": datetime.now().isoformat(),
            "chat": st.session_state.chat_history
        }
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(chat_data, f, indent=2)
        st.success(f"Chat saved to `{filename}`")

# Footer
st.markdown("---")
st.caption(f"🗓️ {datetime.now().strftime('%A, %B %d, %Y')} | Built with ❤️ by Shubhendu")
