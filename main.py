from fastapi import FastAPI
from app.twilio_routes import router

app = FastAPI()

app.include_router(router, prefix="/twilio")

@app.get("/")
def health_check():
    return {"status": "ok"}
