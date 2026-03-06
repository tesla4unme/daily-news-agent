import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import random

# -------- RSS SOURCES --------
RSS_FEEDS = {
    "🌆 Bengaluru": "https://news.google.com/rss/search?q=Bengaluru&hl=en-IN&gl=IN&ceid=IN:en",
    "🏭 Asansol": "https://news.google.com/rss/search?q=Asansol&hl=en-IN&gl=IN&ceid=IN:en",
    "🌉 Kolkata": "https://news.google.com/rss/search?q=Kolkata&hl=en-IN&gl=IN&ceid=IN:en",
    "🌄 Ranchi": "https://news.google.com/rss/search?q=Ranchi&hl=en-IN&gl=IN&ceid=IN:en",
    "🇮🇳 India": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
}

headline_colors = [
"#1a73e8","#c62828","#2e7d32","#6a1b9a",
"#ef6c00","#00838f","#5d4037","#455a64"
]

card_colors = [
"#fdf2f2","#f2f7fd","#f4fbf4","#faf3fd",
"#fff6ed","#f0fafa","#f7f7f7","#fffbea"
]

# -------- TIME FUNCTION --------
def calculate_age(utc_time):

    ist_time = utc_time + timedelta(hours=5, minutes=30)
    now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)

    age = now_ist - ist_time

    minutes = int(age.total_seconds() // 60)
    hours = minutes // 60
    days = hours // 24

    if minutes < 60:
        age_label = f"{minutes}m ago"
    elif hours < 24:
        age_label = f"{hours}h ago"
    else:
        age_label = f"{days}d ago"

    formatted_time = ist_time.strftime("%d %b %Y • %H:%M IST")

    return formatted_time, age_label


# -------- EMAIL HEADER --------
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
📰 News India
</h1>

<p style="text-align:center;color:gray;">
{today_date} • TOTAL_COUNT headlines
</p>

<hr>
"""

count = 1

# -------- PROCESS ALL RSS FEEDS --------
for section, url in RSS_FEEDS.items():

    feed = feedparser.parse(url)

    if len(feed.entries) == 0:
        continue

    articles = []

    for entry in feed.entries:

        if hasattr(entry, "published_parsed") and entry.published_parsed:
            utc_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
        else:
            utc_time = datetime.min

        articles.append((utc_time, entry))

    articles.sort(reverse=True, key=lambda x: x[0])

    html_content += f"<h2 style='margin-top:35px;color:#333;'>{section}</h2>"

    for utc_time, entry in articles[:10]:

        formatted_time, age_label = calculate_age(utc_time)

        publisher = entry.source.title if hasattr(entry,"source") else "Unknown Source"

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
Source: RSS Feeds
</p>

</div>
</body>
</html>
"""

html_content = html_content.replace(
    "TOTAL_COUNT",
    str(count - 1)
)

# -------- EMAIL CONFIG --------
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "📰 News India"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

msg.attach(MIMEText(html_content,"html"))

# -------- SEND EMAIL --------
with smtplib.SMTP("smtp.gmail.com",587) as server:
    server.starttls()
    server.login(sender_email,app_password)
    server.sendmail(sender_email,receiver_email,msg.as_string())

print("Email sent successfully.")
