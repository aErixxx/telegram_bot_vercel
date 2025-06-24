# 🤖 Telegram Bot on Vercel with FastAPI & Aiogram

A full-featured **Telegram Bot** built with **Python**, leveraging **FastAPI** for HTTP routing and **Aiogram** for bot logic. This project is designed for seamless deployment on **Vercel** as a serverless function — no dedicated server required!

> 🧑‍💻 Built by [aErixx](https://github.com/aErixxx) with ❤️

---

## 📌 Overview

This bot supports:

- `/start`, `/help` command handlers
- Echoing user messages
- Handling media (photos, documents, video, audio, voice)
- Smart reply tracking and admin notifications when users reply with `"ok"`
- Easily deployable to **Vercel** with a webhook

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

Telegram: @aErixx

GitHub: aErixx
