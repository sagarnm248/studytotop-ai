# 📚 Snap & Study — StudyToTop AI

An AI-powered study assistant that helps students understand academic materials through conversational AI and image/PDF uploads.

## ✨ Features

- 🤖 **AI Study Assistant:** Ask questions and receive AI-generated explanations using Google Gemini.
- 🖼️ **Image Understanding:** Upload images of study materials and ask questions about them.
- 📄 **PDF Support:** Upload PDF documents for AI-assisted explanations.
- 💬 **Interactive Chat:** Chat with the AI in a simple, user-friendly interface.
- 📲 **WhatsApp Summaries:** Optional study-summary messaging through Twilio when configured.

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Twilio WhatsApp API (optional)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/sagarnm248/studytotop-ai.git
cd studytotop-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Gemini API key

Create a folder named `.streamlit` in the project directory if it does not exist.

Inside it, create a file named `secrets.toml`:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Replace the placeholder with your own API key from [Google AI Studio](https://aistudio.google.com/).

**Security:** Never commit `secrets.toml` or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Your application will open in your browser.

## 🌐 Live Demo

https://studytotop-ai.streamlit.app

## 📁 Project Structure

```text
studytoTop/
├── app.py
├── prompt.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml
```

The `secrets.toml` file is for local configuration only and should not be committed to GitHub.

## 👨‍🎓 Project Purpose

Snap & Study aims to make learning easier and more interactive by helping students explore academic concepts, ask questions, and understand study materials with AI assistance.

## 📄 License

This project was developed for educational and learning purposes.
