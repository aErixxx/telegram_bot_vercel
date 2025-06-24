# 🤖 Telegram Bot on Vercel(Serverless Hosting) with FastAPI & Aiogram

A full-featured **Telegram Bot** built with **Python**, leveraging **FastAPI** for HTTP routing and **Aiogram** for bot logic. This project is designed for seamless deployment on **Vercel** as a serverless function — no dedicated server required!

> 🧑‍💻 Built by [aErixx](https://github.com/aErixxx) with ❤️

---

## 📌 Overview

- Supports `/start`, `/help`, and `/info` commands
- Echoes user messages with additional info such as message length and timestamp
- Handles media: photos, documents, videos, audio, voice messages, and stickers
- Tracks user replies and notifies the admin when a reply contains `"ok"`
- Simple webhook integration compatible with Vercel
- Users can reply with “ok” to the bot, which will then notify the admin confirming that the file or message is correct.
---

## ⚙️ Tech Stack

- 🐍 Python 3.10+
- ⚡ FastAPI (webhook listener)
- 🤖 Aiogram (Telegram Bot Framework)
- ☁️ Vercel (Serverless hosting)
- 🔐 dotenv (Environment management)

---

## 🗂 Project Structure

telegram-bot-vercel/
├── api/
│ └── command.py # Handlers route command
│ └── webhook.py # FastAPI app + Aiogram dispatcher
├── .env # Your Telegram Bot token (not committed)
├── vercel.json # Vercel config for routing & functions
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## 📥 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/telegram-bot-vercel.git
cd telegram-bot-vercel
```
💡 Tips
Don't forget to keep your token secret.

You can monitor logs from Vercel dashboard.

For large bots, consider using a dedicated server with polling instead of webhooks.

🙋‍♂️ Author
Made with ⚡ and ☕ by aErixx

Telegram: @aEl2ixx

GitHub: aErixx
