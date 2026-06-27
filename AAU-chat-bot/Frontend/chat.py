import streamlit as st
import requests

# ------------------------------
# Page Configuration
# ------------------------------
st.set_page_config(
    page_title="AAU AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# Session State
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"


# ------------------------------
# CSS Theme
# ------------------------------
def get_css(theme):

    if theme == "Light":
        return """
        <style>

        /* Whole App */
        .stApp,
        [data-testid="stAppViewContainer"],
        .main,
        .main .block-container {
            background: #ffffff !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"]{
            background:#f3f4f6 !important;
        }

        section[data-testid="stSidebar"] *{
            color:#111827 !important;
        }

        /* Title */
        h1{
            text-align:center;
            color:#4f46e5;
        }

        .subtitle{
            text-align:center;
            color:#6b7280;
        }

        </style>
        """

    else:
        return """
        <style>

        /* Whole App */
        .stApp,
        [data-testid="stAppViewContainer"],
        .main,
        .main .block-container {
            background:#000000 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"]{
            background:#111111 !important;
        }

        section[data-testid="stSidebar"] *{
            color:#e2e8f0 !important;
        }

        /* Title */
        h1{
            text-align:center;
            color:#00fff0;
        }

        .subtitle{
            text-align:center;
            color:#cbd5e1;
        }

        /* Chat input text */
        [data-testid="stChatInput"] input{
            color:white !important;
        }

        </style>
        """


st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:

    try:
        st.image("../assets/aau_logo.png", width=40)
    except:
        st.markdown("### 🎓")

    st.markdown("### AAU Assistant")

    st.divider()

    if st.button("🗑 Clear Chat"):
        try:
            requests.get(f"http://localhost:8000/clear_chat?session_id=user1")
            st.markdown("# chat cleared")
        except:
            st.markdown("# nothing to clear")
        st.session_state.messages = []
        st.session_state.messages = []
        st.rerun()


# ------------------------------
# Main Page
# ------------------------------
st.markdown("# 🎓 AAU General AI Assistant")
st.markdown(
    '<p class="subtitle">Ask anything about Addis Ababa University</p>',
    unsafe_allow_html=True
)

# ------------------------------
# Display Messages
# ------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ------------------------------
# Chat Input
# ------------------------------
if prompt := st.chat_input("Ask me anything about AAU..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        try:
            backend_url = "http://localhost:8000/stream_answer"

            session_id = "user1"

            response = requests.get(
                f"{backend_url}?question={prompt}&session_id={session_id}"
            )

            data = response.json()
            full_response = data["answer"]

            placeholder.markdown(full_response)

        except:
            full_response = "⚠ Backend server is not running."
            placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
