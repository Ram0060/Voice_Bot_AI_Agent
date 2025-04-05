# Voice_Bot_AI_Agent

This project is a voice-enabled conversational AI agent that interacts with users over the phone, transcribes their message using Whisper, responds via OpenAI Assistant API, converts the response to speech using gTTS, and stores the audio reply in a Google Cloud Storage bucket.

💻 Features
📞 Accepts voice calls using Twilio

🧠 Uses OpenAI Assistant API for intelligent response

🗣 Converts assistant replies to speech with gTTS

🧾 Transcribes audio using Whisper ASR

☁️ Uploads final audio reply to Google Cloud Storage

📦 Tech Stack
FastAPI - Backend server

Twilio - Handles incoming calls & recordings

OpenAI - Assistant API (GPT-4)

gTTS - Text-to-speech (Google TTS)

Whisper - Speech-to-text

Google Cloud Storage - Stores assistant reply audio

🔧 Setup Instructions
1. Clone the Repo
bash
Copy
Edit
git clone https://github.com/your-username/voice-ai-agent.git
cd voice-ai-agent
2. Create and Activate Virtual Environment
bash
Copy
Edit
conda create -n voice-ai-agent python=3.10 -y
conda activate voice-ai-agent
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Create .env File
Create a .env file in the root directory with the following values:

ini
Copy
Edit
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
OPENAI_API_KEY=your_openai_key
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/your/voice-agent-gcp-auth.json
GCP_BUCKET_NAME=your-gcp-bucket-name
5. Run the App
bash
Copy
Edit
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
