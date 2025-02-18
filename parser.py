from collections import Counter
import pandas as pd
import re
import emoji

# Function to parse the chat log
def parse_chat_log(contents):
    pattern1 = re.compile(r"(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s?[APM]*?) - ([^:]+?): (.*)")
    pattern2 = re.compile(r"\[(\d{2}/\d{2}/\d{2}), (\d{1,2}:\d{2}:\d{2}\s?[APM]*)\] ([^:]+): (.*)")
    
    excluded_messages = {"GIF omitted", "video omitted", "image omitted", "audio omitted", "document omitted", "Media omitted"}
    data = []
    lines = contents.decode("utf-8").split("\n")
    
    for line in lines:
        match = pattern1.match(line.strip()) or pattern2.match(line.strip())
        if match:
            date, time, person, message = match.groups()
            message = message.strip('"')
            if message not in excluded_messages:
                data.append([date, time, person, message])
        else:
            if data and data[-1][3] not in excluded_messages:
                data[-1][3] += '\n' + line.strip()
    
    df = pd.DataFrame(data, columns=['Date', 'Time', 'Person', 'Message'])
    df = df[~df['Message'].str.contains("omitted", case=False, na=False)]
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], errors='coerce')
    return df

# Function to count "sorry" messages
def count_sorry_messages(df):
    sorry_variants = ["sorry", "sry", "my bad", "apologies"]
    sorry_regex = re.compile('|'.join(sorry_variants), re.IGNORECASE)
    
    sorry_counts = df.groupby("Person")["Message"].apply(lambda messages: sum(bool(sorry_regex.search(msg)) for msg in messages)).to_dict()
    print("Sorry count done")
    return sorry_counts

# Function to find the most used word with more than 4 letters per person
def most_used_important_word(df):
    word_counts = {}
    
    for person, messages in df.groupby("Person")["Message"]:
        words = " ".join(messages).lower().split()
        filtered_words = [word for word in words if word.isalpha() and len(word) > 4]
        word_freq = Counter(filtered_words)
        most_common_word = word_freq.most_common(1)[0] if word_freq else ("None", 0)
        word_counts[person] = most_common_word
    print("Most used important word done")
    return word_counts

# Function to format seconds into human-readable time
def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours} hr {minutes} min {seconds} sec"
    elif minutes:
        return f"{minutes} min {seconds} sec"
    else:
        return f"{seconds} sec"

# Function to find the fastest and slowest reply times
def fastest_slowest_reply(df):
    df = df.sort_values(by='Datetime')
    df['Prev_Datetime'] = df['Datetime'].shift(1)
    df['Prev_Person'] = df['Person'].shift(1)
    df['Time_Diff'] = (df['Datetime'] - df['Prev_Datetime']).dt.total_seconds()

    valid_replies = df[df['Person'] != df['Prev_Person']]
    if valid_replies.empty:
        return {"fastest": "None", "slowest": "None"}

    fastest_idx = valid_replies['Time_Diff'].idxmin()
    slowest_idx = valid_replies['Time_Diff'].idxmax()

    fastest = valid_replies.loc[fastest_idx]
    slowest = valid_replies.loc[slowest_idx]

    print("Reply time analysis done")
    return {
        "fastest": (fastest["Person"], format_time(fastest["Time_Diff"])),
        "slowest": (slowest["Person"], format_time(slowest["Time_Diff"]))
    }

# Function to calculate average reply time per person
def average_reply_time(df):
    df = df.sort_values(by='Datetime')
    df['Prev_Datetime'] = df['Datetime'].shift(1)
    df['Prev_Person'] = df['Person'].shift(1)
    df['Time_Diff'] = (df['Datetime'] - df['Prev_Datetime']).dt.total_seconds()

    valid_replies = df[(df['Person'] != df['Prev_Person']) & (df['Time_Diff'] <= 18000)]
    avg_times = valid_replies.groupby('Person')['Time_Diff'].mean().fillna(0).apply(format_time)

    print("Average reply time done")
    return avg_times.to_dict()

# Function to find the most used emoji per person
def most_used_emoji(df):
    emoji_counts = {}
    
    for person, messages in df.groupby("Person")["Message"]:
        emojis = [char for msg in messages for char in msg if char in emoji.EMOJI_DATA]
        emoji_freq = Counter(emojis)
        most_common_emoji = emoji_freq.most_common(1)[0] if emoji_freq else ("None", 0)
        emoji_counts[person] = most_common_emoji
    print("Most used emoji analysis done")
    return emoji_counts

# Function to count "I love you" messages
def count_love_messages(df):
    love_variants = ["i love you", "i luv u", "i luv you", "i love u", "ily", "i lub you", "i lub u"]
    love_regex = re.compile('|'.join(love_variants), re.IGNORECASE)
    
    love_counts = df.groupby("Person")["Message"].apply(lambda messages: sum(bool(love_regex.search(msg)) for msg in messages)).to_dict()
    print("Love message count done")
    return love_counts

# Function to count "I miss you" messages
def count_miss_messages(df):
    miss_variants = ["i miss you", "i miss u"]
    miss_regex = re.compile('|'.join(miss_variants), re.IGNORECASE)
    
    miss_counts = df.groupby("Person")["Message"].apply(lambda messages: sum(bool(miss_regex.search(msg)) for msg in messages)).to_dict()
    print("Miss message count done")
    return miss_counts

# Function to find the most affectionate hour
def most_lovey_dovey_hour(df):
    love_keywords = ["i love you", "i miss you", "i adore you", "love u", "miss u", "ily", "i heart you"]
    love_emojis = {"❤️", "💖", "💕", "💞", "😍", "😘", "💓", "🥰"}

    love_regex = re.compile('|'.join(love_keywords), re.IGNORECASE)
    df["Hour"] = df["Datetime"].dt.hour

    love_hour_count = Counter()

    for _, row in df.iterrows():
        message = row["Message"]
        hour = row["Hour"]

        if love_regex.search(message) or any(char in love_emojis for char in message):
            love_hour_count[hour] += 1

    if love_hour_count:
        most_lovey_hour = max(love_hour_count, key=love_hour_count.get)
        print("Most Lovey-Dovey Hour analysis done")
        return f"💖 Most Lovey-Dovey Hour: {most_lovey_hour}:00 - {most_lovey_hour + 1}:00 ({love_hour_count[most_lovey_hour]} love messages)"
    else:
        return "No love messages found 😢"

