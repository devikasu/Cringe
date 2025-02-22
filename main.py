from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from parser import (
    parse_chat_log, 
    most_used_important_word, 
    count_love_messages, 
    longest_message, 
    most_used_emoji, 
    count_sorry_messages, 
    average_reply_time, 
    fastest_slowest_reply, 
    same_minute_reply_count,
    count_miss_messages
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

executor = ThreadPoolExecutor(max_workers=8)  # Adjust based on CPU cores

@app.get("/", response_class=HTMLResponse)
def serve_form():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

async def analyze_chat(df):
    """
    Runs chat analysis functions concurrently using asyncio.
    """
    loop = asyncio.get_event_loop()

    try:
        # Run multiple computations in parallel
        results = await asyncio.gather(
            loop.run_in_executor(executor, most_used_important_word, df),
            loop.run_in_executor(executor, count_love_messages, df),
            loop.run_in_executor(executor, longest_message, df),
            loop.run_in_executor(executor, most_used_emoji, df),
            loop.run_in_executor(executor, count_sorry_messages, df),
            loop.run_in_executor(executor, average_reply_time, df),
            loop.run_in_executor(executor, fastest_slowest_reply, df),
            loop.run_in_executor(executor, same_minute_reply_count, df),
            loop.run_in_executor(executor, count_miss_messages, df)
        )

        # Extract results safely
        longest_msg = results[2] if isinstance(results[2], list) and results[2] else [["No messages found", ""]]

        return {
            "most_used_word": results[0],
            "love_counts": results[1],
            "longest_message": longest_msg,  # ✅ Always valid
            "emoji_data": results[3],
            "sorry": results[4],
            "replies": results[5],
            "speed": results[6],
            "minute": results[7],
            "miss": results[8]
        }
    
    except Exception as e:
        print(f"Error analyzing chat: {e}")
        return {
            "most_used_word": {},
            "love_counts": {},
            "longest_message": [["No messages found", ""]],
            "emoji_data": {},
            "sorry": {},
            "replies": {},
            "speed": {},
            "minute": {},
            "miss": {}
        }

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    Handles file upload and processes the chat log efficiently.
    """
    try:
        # Read file in chunks instead of all at once
        contents = await file.read()

        # Process chat log in a separate thread
        df = await asyncio.get_event_loop().run_in_executor(executor, parse_chat_log, contents)

        # Run chat analysis in parallel
        results = await analyze_chat(df)

        # ✅ Ensure all variables are valid before rendering the template
        return templates.TemplateResponse("dashboard.html", {"request": request, **results})
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return HTMLResponse(content="<h2>Something went wrong while processing the file.</h2>", status_code=500)
