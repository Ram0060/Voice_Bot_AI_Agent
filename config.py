import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "https://your-ngrok-or-domain.com")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("Twilio credentials not found.")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found.")

if not GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is missing or path is invalid.")

if not GCP_BUCKET_NAME:
    raise ValueError("GCP_BUCKET_NAME not set.")
