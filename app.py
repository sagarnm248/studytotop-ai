from google import genai
from google.genai import types
import streamlit as st
from twilio.rest import Client as TwilioClient

from prompt import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)

# ============================================================
# CONFIG
# ============================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

TWILIO_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = st.secrets.get("TWILIO_WHATSAPP_FROM", "")
TWILIO_CONTENT_SID = st.secrets.get("TWILIO_CONTENT_SID", "")

TWILIO_ENABLED = all([
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    TWILIO_CONTENT_SID,
])


# ============================================================
# CLIENTS
# ============================================================

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


@st.cache_resource
def get_twilio_client():
    if not TWILIO_ENABLED:
        return None

    return TwilioClient(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )


gemini_client = get_gemini_client()
twilio_client = get_twilio_client()

MODEL_NAME = "gemini-3.5-flash"



# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."

    text = " ".join(text.split())

    return text[:1500] + "..." if len(text) > 1500 else text


def send_summary_to_phone(user_name, to_phone_number, summary):
    if not TWILIO_ENABLED or twilio_client is None:
        return False, "WhatsApp is not configured yet."

    import json

    try:
        content_variables = {
            "1": user_name,
            "2": clean_whatsapp_text(summary),
        }

        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_phone_number}",
            content_sid=TWILIO_CONTENT_SID,
            content_variables=json.dumps(
                content_variables,
                ensure_ascii=False
            ),
        )

        return True, message.sid

    except Exception as error:
        return False, str(error)

def render_message(message):
    with st.chat_message(message["role"]):

        if message["kind"] == "text":
            st.markdown(message["content"])

        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    message = {
        "role": role,
        "kind": kind,
        "content": content,
    }

    st.session_state.messages.append(message)

    render_message(message)


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text

    except Exception as error:
        return f"Sorry, something went wrong: {error}"


# ============================================================
# STEP 1: ONBOARDING
# ============================================================

if not st.session_state.onboarded:

    st.title("StudyToTop 📚")
    st.caption("Snap & Study")

    with st.form("onboarding_form"):

        st.subheader(
            "Welcome to StudyToTop! Let's get you started."
        )

        name = st.text_input("What's your name?")
        phone_number = st.text_input("What's your phone number?")

        submitted = st.form_submit_button(
            "Start new journey"
        )

        if submitted:

            if not name or not phone_number:
                st.error("Please fill in both fields.")

            else:
                # Save user information
                st.session_state.name = name.strip()
                st.session_state.phone_number = phone_number.strip()

                # Create Gemini chat
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )

                # Reset messages for new journey
                st.session_state.messages = []

                # Mark onboarding complete
                st.session_state.onboarded = True

                st.success(
                    f"Thanks {name}! You're all set to start studying."
                )

                st.rerun()

    # IMPORTANT:
    # Stop execution here until onboarding is complete.
    st.stop()


# ============================================================
# MAIN CHAT INTERFACE
# ============================================================

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


with header_col:
    st.title("StudyToTop 📚")
    st.caption("Snap & Study")


# ============================================================
# WHATSAPP BUTTON
# ============================================================

with button_col:

    send_disabled = len(st.session_state.messages) <= 2

    if st.button(
        "📤 Send to WhatsApp",
        disabled=send_disabled,
        use_container_width=True,
    ):

        with st.spinner("Summarizing your day..."):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

        # IMPORTANT:
        # Function expects:
        # send_summary_to_phone(user_name, phone_number, summary)

        success, info = send_summary_to_phone(
            st.session_state.name,
            st.session_state.phone_number,
            summary,
        )

        if success:
            st.success("Sent! Check your WhatsApp 📲")

        else:
            st.error(
                f"Couldn't send that: {info}"
            )


# ============================================================
# USER INFO
# ============================================================

st.caption(
    f"Logged in as {st.session_state.name} - "
    f"updates go to {st.session_state.phone_number}"
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        ),
    )

else:

    for message in st.session_state.messages:
        render_message(message)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Type your question or upload an image here...",
    accept_file=True,
    file_type=[
        "png",
        "jpg",
        "jpeg",
        "pdf",
    ],
)


if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text.strip()

    parts = []


    # --------------------------------------------------------
    # IMAGE / PDF
    # --------------------------------------------------------

    if photo is not None:

        photo_bytes = photo.getvalue()

        add_message(
            "user",
            "image",
            photo_bytes,
        )

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )


    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    if text:

        add_message(
            "user",
            "text",
            text,
        )

        parts.append(text)

    elif photo is not None:

        parts.append(
            "Please explain the content of the uploaded image."
        )


    # --------------------------------------------------------
    # GEMINI RESPONSE
    # --------------------------------------------------------

    with st.spinner("Generating explanation..."):

        answer = ask_gemini(parts)

    add_message(
        "assistant",
        "text",
        answer,
    )
