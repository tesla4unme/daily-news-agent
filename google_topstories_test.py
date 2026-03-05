import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import random

# -------- SETTINGS --------
RSS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

city_feeds = {
    "🌆 Bengaluru": "https://news.google.com/rss/search?q=Bengaluru&hl=en-IN&gl=IN&ceid=IN:en",
    "🏭 Asansol": "https://news.google.com/rss/search?q=Asansol&hl=en-IN&gl=IN&ceid=IN:en",
    "🌉 Kolkata": "https://news.google.com/rss/search?q=Kolkata&hl=en-IN&gl=IN&ceid=IN:en",
    "🌄 Ranchi": "https://news.google.com/rss/search?q=Ranchi&hl=en-IN&gl=IN&ceid=IN:en"
}

headline_colors = [
"#1a73e8","#c62828","#2e7d32","#6a1b9a",
"#ef6c00","#00838f","#5d4037","#455a64"
]

card_colors = [
"#fdf2f2",
"#f2f7fd",
"#f4fbf4",
"#faf3fd",
"#fff6ed",
"#f0fafa",
"#f7f7f7",
"#fffbea"
]

# -------- FETCH MAIN FEED --------
feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("No news items found.")
    exit()

# -------- SORT ARTICLES BY TIME --------
articles = []

for entry in feed.entries:

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        utc_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
    else:
        utc_time = datetime.min

    articles.append((utc_time, entry))

articles.sort(reverse=True, key=lambda x: x[0])

# -------- CATEGORY KEYWORDS --------
categories = {
    "🌍 Geopolitics": ["war","iran","china","russia","israel","military","conflict","nuclear"],
    "📈 Markets": ["market","stock","shares","profit","loss","lng","oil","gold","economy","bank"],
    "🧬 Science & Tech": ["science","research","ai","technology","study","medical","virus"],
    "🎬 Entertainment": ["film","movie","actor","box office","bollywood","hollywood","trailer"]
}

grouped = {cat: [] for cat in categories}
grouped["📰 Other"] = []

# -------- GROUP ARTICLES --------
for utc_time, entry in articles:

    title_lower = entry.title.lower()
    placed = False

    for cat, keywords in categories.items():
        if any(word in title_lower for word in keywords):
            grouped[cat].append((utc_time, entry))
            placed = True
            break

    if not placed:
        grouped["📰 Other"].append((utc_time, entry))

# -------- HEADER INFO --------
today_date = datetime.now().strftime("%d %B %Y")
# total_news = len(articles)

# -------- BUILD EMAIL --------
html_content = f"""
<html>
<body style="font-family:Arial, sans-serif;background:#f4f6f8;padding:20px;">

<div style="
max-width:760px;
margin:auto;
background:white;
padding:25px;
border-radius:12px;
box-shadow:0 4px 14px rgba(0,0,0,0.08);
">

<h1 style="text-align:center;margin-bottom:5px;">
📰 News India
</h1>

<p style="text-align:center;color:gray;">
{today_date} • TOTAL_COUNT  headlines
</p>

<hr>
"""

count = 1

# -------- CITY NEWS SECTIONS --------
for city, url in city_feeds.items():

    city_feed = feedparser.parse(url)

    if len(city_feed.entries) == 0:
        continue

    html_content += f"<h2 style='margin-top:35px;color:#333;'>{city}</h2>"

    for entry in city_feed.entries[:5]:

        if hasattr(entry, "published_parsed") and entry.published_parsed:
            utc_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            ist_time = utc_time + timedelta(hours=5, minutes=30)

            now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)

            age = now_ist - ist_time
            hours = int(age.total_seconds() // 3600)
            minutes = int((age.total_seconds() % 3600) // 60)

            if hours > 0:
                age_label = f"{hours}h ago"
            else:
                age_label = f"{minutes}m ago"

            formatted_time = ist_time.strftime("%d %b %Y • %H:%M IST")

        else:
            formatted_time = "Time not available"
            age_label = ""

        if hasattr(entry, "source"):
            publisher = entry.source.title
        else:
            publisher = "Unknown Source"

        card_color = random.choice(card_colors)
        headline_color = random.choice(headline_colors)

        html_content += f"""
        <div style="
        background:{card_color};
        padding:15px;
        margin-bottom:12px;
        border-radius:8px;
        border:1px solid #e6e6e6;
        border-left:4px solid #1a73e8;
        ">

        <b>{count}. <a href="{entry.link}" style="
        text-decoration:none;
        color:{headline_color};
        font-size:17px;
        line-height:1.35;
        ">
        {entry.title}
        </a></b>

        <br><br>

        <span style="
        font-size:12px;
        color:#666;
        background:#eef2f7;
        padding:3px 7px;
        border-radius:4px;
        ">
        {publisher} • {formatted_time} • {age_label}
        </span>

        </div>
        """

        count += 1
        
# -------- BUILD STORY CARDS --------
for category, items in grouped.items():

    if len(items) == 0:
        continue

    html_content += f"<h2 style='margin-top:35px;color:#333;'>{category}</h2>"

    for utc_time, entry in items:

        if utc_time != datetime.min:
            ist_time = utc_time + timedelta(hours=5, minutes=30)
            now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)

            age = now_ist - ist_time
            hours = int(age.total_seconds() // 3600)
            minutes = int((age.total_seconds() % 3600) // 60)

            if hours > 0:
                age_label = f"{hours}h ago"
            else:
                age_label = f"{minutes}m ago"

            formatted_time = ist_time.strftime("%d %b %Y • %H:%M IST")

        else:
            formatted_time = "Time not available"
            age_label = ""

        if hasattr(entry, "source"):
            publisher = entry.source.title
        else:
            publisher = "Unknown Source"

        card_color = random.choice(card_colors)
        headline_color = random.choice(headline_colors)

        html_content += f"""
        <div style="
        background:{card_color};
        padding:15px;
        margin-bottom:12px;
        border-radius:8px;
        border:1px solid #e6e6e6;
        border-left:4px solid #1a73e8;
        ">

        <b>{count}. <a href="{entry.link}" style="
        text-decoration:none;       
        color:{headline_color};
        font-size:17px;
        line-height:1.35;
        ">
        {entry.title}
        </a></b>

        <br><br>

        <span style="
        font-size:12px;
        color:#666;
        background:#eef2f7;
        padding:3px 7px;
        border-radius:4px;
        ">
        {publisher} • {formatted_time} • {age_label}
        </span>

        </div>
        """

        count += 1

html_content += """
<hr>

<p style="
font-size:12px;
color:gray;
text-align:center;
">
Source: Google News India RSS
)
</p>

</div>
</body>
</html>
"""
html_content = html_content.replace(
    "TOTAL_COUNT",
    str(count - 1)
    
# -------- EMAIL CONFIG --------
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "📰 News India"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

msg.attach(MIMEText(html_content, "html"))

# -------- SEND EMAIL --------
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully.")
