import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time

# -------- SETTINGS --------
RSS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

# -------- FETCH FEED --------
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

# -------- BUILD EMAIL --------
today_date = datetime.now().strftime("%d %B %Y")

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
📰 India Morning Intelligence
</h1>

<p style="text-align:center;color:gray;">
{today_date}
</p>

<hr>
"""

count = 1

# -------- BUILD STORY CARDS --------
for category, items in grouped.items():

    if len(items) == 0:
        continue

    html_content += f"<h2 style='margin-top:35px;color:#333;'>{category}</h2>"

    for utc_time, entry in items:

        # Convert UTC → IST
        if utc_time != datetime.min:
            ist_time = utc_time + timedelta(hours=5, minutes=30)
            formatted_time = ist_time.strftime("%d %b %Y • %H:%M IST")
        else:
            formatted_time = "Time not available"

        # Publisher extraction
        if hasattr(entry, "source"):
            publisher = entry.source.title
        else:
            publisher = "Unknown Source"

        # Alternate card color
        card_color = "#ffffff" if count % 2 == 0 else "#f8f9fb"

        html_content += f"""
        <div style="
        background:{card_color};
        padding:15px;
        margin-bottom:12px;
        border-radius:8px;
        border:1px solid #e6e6e6;
        ">

        <b>{count}. <a href="{entry.link}" style="
        text-decoration:none;
        color:#1a73e8;
        font-size:17px;
        ">
        {entry.title}
        </a></b>

        <br>

        <span style="
        font-size:12px;
        color:#666;
        ">
        {publisher} • {formatted_time}
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
</p>

</div>
</body>
</html>
"""

# -------- EMAIL CONFIG --------
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "📰 India Morning Intelligence"

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
