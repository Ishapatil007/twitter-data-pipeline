import csv
import re
import sqlite3
import matplotlib.pyplot as plt
from textblob import TextBlob

# Sentiment function
def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Connect DB
conn = sqlite3.connect("tweets.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tweets (
    id TEXT,
    username TEXT,
    tweet TEXT,
    clean_tweet TEXT,
    sentiment TEXT,
    date TEXT
)
""")

# Read CSV
with open("twitter_dataset.csv", newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)

    for i, row in enumerate(reader):
        if i > 200:
            break

        # Extract hashtags
        hashtags = re.findall(r"#(\w+)", row[2])
        print("Hashtags:", hashtags)

        # Clean tweet
        clean_tweet = re.sub(r"http\S+|@\w+|#", "", row[2])
        clean_tweet = re.sub(r"[^A-Za-z ]", "", clean_tweet).lower()

        # Sentiment
        sentiment = get_sentiment(clean_tweet)

        print("Processed Tweet:", clean_tweet)
        print("Sentiment:", sentiment)

        # Insert into DB
        cursor.execute(
            "INSERT INTO tweets VALUES (?, ?, ?, ?, ?, ?)",
            (row[0], row[1], row[2], clean_tweet, sentiment, row[5])
        )

# Save
conn.commit()
print("Data stored successfully!")

# Query: Top users
cursor.execute("""
SELECT username, COUNT(*) 
FROM tweets 
GROUP BY username 
ORDER BY COUNT(*) DESC 
LIMIT 5;
""")

data = cursor.fetchall()

# Visualization 1
users = [row[0] for row in data]
counts = [row[1] for row in data]

plt.figure(figsize=(8,5))
plt.bar(users, counts)
plt.title("Top Active Users")
plt.xlabel("Users")
plt.ylabel("Tweet Count")
plt.xticks(rotation=30)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("top_users.png")
print("Graph saved: top_users.png")

# Visualization 2 (Sentiment)
cursor.execute("""
SELECT sentiment, COUNT(*) 
FROM tweets 
GROUP BY sentiment;
""")

sent_data = cursor.fetchall()

labels = [row[0] for row in sent_data]
counts = [row[1] for row in sent_data]

plt.figure()
plt.pie(counts, labels=labels, autopct='%1.1f%%')
plt.title("Sentiment Distribution")
plt.savefig("sentiment.png")
print("Graph saved: sentiment.png")

# Close DB
conn.close()