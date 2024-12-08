import streamlit as st
import requests

# Initialize session state variables
if 'response_data' not in st.session_state:
    st.session_state.response_data = None
if 'translation_required' not in st.session_state:
    st.session_state.translation_required = False

# Streamlit UI
st.title("Smart Learning With GenAI")
# Add an image below the title
st.image(r"C:\Users\6130180\OneDrive - Thomson Reuters Incorporated\Desktop\Screenshot 2024-12-07 210920.png",
         use_container_width=True)

# First form for initial input
with st.form("agent_form"):
    subject = st.selectbox("Subject", ["Science", "Comics"])
    topic = st.text_input("Topic")
    age = st.number_input("Grade", min_value=1, max_value=12)
    activity = st.selectbox("Activity", ["Summarization", "Teaching", "Evaluation"])
    # Default value
    learner_type = st.selectbox("Learning Type", ["Kinesthetic", "Visual", "Auditory", "Reading/Writing"])
    audio_book_required = st.checkbox("Audio Format Required")
    submitted = st.form_submit_button("Submit")

if submitted:
    if not subject or not activity:
        st.error("Missing required fields: subject and activity")
    else:
        payload = {
            'subject': subject,
            'topic': topic,
            'age': age,
            'learner-type': learner_type,
            'activity': activity,
            'audio-book-required': audio_book_required,
        }

        try:
            response = requests.post(
                'https://ee2lhsu6kk2rjigf7ynzybqs4u0ifocn.lambda-url.us-west-2.on.aws/get_response', json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            if response.headers['Content-Type'] == 'audio/mpeg':
                audio_content = response.content
                st.audio(audio_content, format='audio/mp3')
            else:
                st.session_state.response_data = response.json()
                st.success("Agent Response:")
                st.write(st.session_state.response_data["response"])
        except requests.exceptions.RequestException as e:
            st.error(f"Error invoking backend: {str(e)}")

# Display translation options if we have a response
if st.session_state.response_data:
    st.session_state.translation_required = st.checkbox("Translation Required",
                                                        value=st.session_state.translation_required)

    if st.session_state.translation_required:
        st.markdown("""
                <style>
                .tooltip {
                    position: relative;
                    display: inline-block;
                    cursor: pointer;
                }

                .tooltip .tooltiptext {
                    visibility: hidden;
                    width: 200px;
                    background-color: #555;
                    color: #fff;
                    text-align: center;
                    border-radius: 6px;
                    padding: 5px;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%; /* Position the tooltip above the text */
                    left: 50%;
                    margin-left: -100px;
                    opacity: 0;
                    transition: opacity 0.3s;
                }

                .tooltip:hover .tooltiptext {
                    visibility: visible;
                    opacity: 1;
                }
                </style>
                """, unsafe_allow_html=True)

        st.markdown("""
                <div class="tooltip">ℹ️
                    <span class="tooltiptext">Available language codes: en (English), hi(Hindi), es (Spanish), fr (French), de (German), etc.</span>
                </div>
                """, unsafe_allow_html=True)
        translation_language = st.text_input("Translation Language (e.g., es for Spanish)")
        translate_submitted = st.button("Translate")

        if translate_submitted:
            translation_payload = {
                'translate-required': True,
                'translate-query': st.session_state.response_data['response'],
                'target-language': translation_language
            }
            try:
                translation_response = requests.post(
                    'https://mj2vxyyd4ii5jib462ejtzfgjm0efdze.lambda-url.us-west-2.on.aws/translate',
                    json=translation_payload)
                translation_response.raise_for_status()  # Raise an error for bad status codes
                translation_data = translation_response.json()
                st.success("Source Text:")
                st.write(st.session_state.response_data['response'])
                st.success("Translated Response:")
                st.write(translation_data['translated_text'])
            except requests.exceptions.RequestException as e:
                st.error(f"Error invoking translation: {str(e)}")