import os
import sys
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Telegram Bot is running!",
        "status": "OK",
        "has_token": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "python_version": sys.version
    }

@app.post("/webhook")  
async def webhook(request: Request):
    try:
        data = await request.json()
        return {"ok": True, "received": True}
    except Exception as e:
        return {"error": str(e)}

# For Vercel
handler = app
