import streamlit as st
from openai import OpenAI
import os
from datetime import datetime
import json
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Please set the OPENAI_API_KEY in your Streamlit Secrets.")
    st.stop()

# App title and description
st.title("Medical-Legal Assistant for Doctors in India")
st.markdown("""
This chatbot provides legal guidance to doctors in India to help avoid legal troubles.  
Upload files (e.g., consent forms, legal notices) for analysis, and get advice with references to Indian laws and guidelines.  
**Note**: This is for informational purposes only—not legal advice. Always consult a qualified legal professional.
""")

# Sidebar with law summary
with st.sidebar:
    st.header("Key Indian Medical Laws")
    st.markdown("""
    - **Indian Medical Council Act, 1956**: Governs medical practice and ethics (MCI Regulations, 2002).
    - **Consumer Protection Act, 2019**: Addresses negligence and deficiency in service.
    - **Clinical Establishments Act, 2010**: Mandates consent and record-keeping.
    - **NDPS Act, 1985**: Regulates controlled substances.
    - **IT Act, 2000**: Protects patient data privacy.
    - **Landmark Cases**: *Samira Kohli (2008)* - Consent; *Jacob Mathew (2005)* - Negligence.
    """)

# Disclaimer checkbox
if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.warning("Please accept the disclaimer to proceed.")
    if st.checkbox("I understand this is not legal advice and will consult a professional for specific cases."):
        st.session_state.disclaimer_accepted = True

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
if st.session_state.disclaimer_accepted:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File upload section
    uploaded_file = st.file_uploader("Upload a file (e.g., consent form, legal notice)", type=["pdf", "txt", "docx"])
    file_id = None
    if uploaded_file:
        with st.spinner("Uploading file..."):
            file_obj = client.files.create(
                file=uploaded_file,
                purpose="user_data"
            )
            file_id = file_obj.id
            st.success(f"File uploaded successfully: {uploaded_file.name}")

    # User input
    user_input = st.chat_input("Enter your medical-legal query (e.g., 'Is written consent needed for surgery?')")

    if user_input and st.session_state.disclaimer_accepted:
        with st.chat_message("user"):
            st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Fetching response..."):
            try:
                messages = [
                    {
                        "role": "system",
                        "content": """
                        You are an AI expert in Indian medical-legal cases, assisting doctors to avoid legal troubles.  
                        Provide detailed, in-depth guidance with references to Indian laws (e.g., Indian Medical Council Act, 1956; Consumer Protection Act, 2019; Clinical Establishments Act, 2010; NDPS Act, 1985; IT Act, 2000) and multiple relevant landmark judgments (e.g., Samira Kohli vs. Dr. Prabha Manchanda, 2008; Jacob Mathew vs. State of Punjab, 2005; V. Shantha vs. Indian Medical Association, 1995) to illustrate legal principles.  
                        If a file is uploaded (e.g., consent form), analyze it thoroughly and check compliance with legal standards, citing specific clauses or cases.  
                        Offer practical steps doctors can take and emphasize that this is not legal advice—doctors should consult professionals for specific cases.
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

                bot_response = response.choices[0].message.content.strip()

                with st.chat_message("assistant"):
                    st.markdown(bot_response)
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Save Chat button
    if st.button("Save Chat"):
        chat_data = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": st.session_state.chat_history
        }
        with open(f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(chat_data, f)
        st.success("Chat saved successfully!")

# Footer
st.markdown(f"Current date: {datetime.now().strftime('%B %d, %Y')}")