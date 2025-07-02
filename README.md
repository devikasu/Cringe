# 💌 Valentine Chat Analyzer

A fun, romantic chat analysis web app built using **FastAPI** and **Jinja2**. Upload your exported WhatsApp chat to get adorable insights like who says "I love you" the most, average reply times, favorite emojis, and more.

---

## ✨ Features

- ❤️ Count how many times each person says **"I love you"**
- 😢 Track **"I miss you"** messages
- 🙇 Count apology messages like **"sorry"**, **"sry"**, etc.
- 😂 Find the most used emoji by each person
- ✍️ Detect the **longest message** overall and per person
- ⏱️ Measure **fastest and slowest replies**
- 🕒 Show **average reply time** per person
- ⏰ Count replies sent within the **same minute**
- 🧠 Identify the **most used word** (with more than 4 letters)

---

## 📁 Project Structure

├── app.py # FastAPI app
├── parser.py # Chat analysis logic
├── templates/
│ ├── index.html # Upload page
│ └── dashboard.html # Dashboard page
├── requirements.txt # All dependencies
└── README.md # You're reading it!

Install dependencies
pip install -r requirements.txt
Or manually:
pip install fastapi uvicorn pandas jinja2 python-multipart emoji

Exporting WhatsApp Chat
Open your chat in WhatsApp

Tap on 3 dots → More → Export chat

Choose "Without media"

Send the .txt file to your laptop

Upload it on the site!