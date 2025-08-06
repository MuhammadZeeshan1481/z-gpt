# Z-GPT: AI Assistant with Chat, Image Generation, and Translation

Z-GPT is a full-stack AI assistant built using FastAPI for the backend and React for the frontend. It supports natural language conversations, image generation from prompts, and multilingual translation with automatic language detection.

## Features

- Chatbot using Hugging Face Transformers
- Prompt-based image generation using Diffusers
- Language detection and translation using Argos Translate
- Multilingual input/output with seamless translation handling
- Clean React-based UI with Bootstrap styling

## Backend Setup (FastAPI)

1. Clone the repository:

git clone https://github.com/your-username/z-gpt.git
cd z-gpt


2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate


3. Install Python dependencies:
pip install -r requirements.txt


4. Run the backend server:
uvicorn backend.main:app --reload


## Frontend Setup (React)

1. Navigate to the frontend directory:
cd frontend


2. Install npm dependencies:
npm start


Frontend will be served at `http://localhost:3000` and it will interact with the backend running at `http://localhost:8000`.

## API Overview

### POST /chat/
- Accepts a message and optional history
- Detects language and translates to English if needed
- Sends to LLM and returns translated response

### POST /image/
- Accepts a prompt string
- Returns a generated image in base64 format

### POST /translate/
- Accepts text, source language code, and target language code
- Returns translated text

## Requirements

All dependencies are listed in `requirements.txt`. Major libraries used include:

- fastapi
- uvicorn
- python-multipart
- transformers
- torch
- accelerate
- peft
- sentencepiece
- huggingface-hub
- langchain
- chromadb
- faiss-cpu
- diffusers
- safetensors
- Pillow
- argostranslate
- langdetect
- streamlit
- notebook
- python-dotenv

## Sample Prompts

- Who was the first prime minister of Pakistan?
- Generate an image of a crescent moon over a desert night in Pakistan
- پاکستان کا پہلا وزیراعظم کون تھا؟
- Tell me in French why Paris is famous

## License

This project is licensed under the MIT License.
