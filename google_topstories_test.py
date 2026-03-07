import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import random

# ======================================
# CONFIGURATION
# ======================================

CATEGORIES = {

    "🇮🇳 INDIA": {

        "feeds": [

            {
                "url": "https://www.thehindu.com/news/national/feeder/default.rss",
                "max_age_hours": 6,
                "max_items": 10
            },

            {
                "url": "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
                "max_age_hours": 6,
                "max_items": 10
            },

            {
                "url": "https://news.google.com/rss/search?q=India&hl=en-IN&gl=IN&ceid=IN:en",
                "max_age_hours": 6,
                "max_items": 20
            }

        ]
    }

}

# ======================================
# STYLE SETTINGS
# ======================================

headline_colors = [
"#1a73e8","#c62828","#2e7d32","#6a1b9a",
"#ef6c00","#00838f","#5d4037","#455a64"
]

card_colors = [
"#fdf2f2","#f2f7fd","#f4fbf4","#faf3fd",
"#fff6ed","#f0fafa","#f7f7f7","#fffbea"
]

# ======================================
# TIME FORMAT FUNCTION
# ======================================

def format_age(utc_time):

    ist_time = utc_time + timedelta(hours=5, minutes=30)
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)

    age = now - ist_time

    minutes = int(age.total_seconds() / 60)
    hours = int(minutes / 60)
    days = int(hours / 24)

    if minutes < 60:
        age_label = f"{minutes}m ago"
    elif hours < 24:
        age_label = f"{hours}h ago"
    else:
        age_label = f"{days}d ago"

    formatted_time = ist_time.strftime("%d %b %Y • %H:%M IST")

    return formatted_time, age_label

# ======================================
# BUILD EMAIL HEADER
# ======================================

today = datetime.now().strftime("%d %B %Y")

html = f"""
<html>
<body style="font-family:Arial;background:#f4f6f8;padding:20px;">

<div style="
max-width:760px;
margin:auto;
background:white;
padding:25px;
border-radius:12px;
box-shadow:0 4px 14px rgba(0,0,0,0.08);
">

<h1 style="text-align:center">📰 Daily Intelligence Brief</h1>
<p style="text-align:center;color:gray;">{today}</p>
<hr>
"""

count = 1

# ======================================
# PROCESS CATEGORIES
# ======================================

for category, config in CATEGORIES.items():

    articles = []
    now = datetime.utcnow()

    for feed_cfg in config["feeds"]:

        url = feed_cfg["url"]
        max_age = feed_cfg["max_age_hours"]
        max_items = feed_cfg["max_items"]

        feed = feedparser.parse(url)

        items_added = 0

        for entry in feed.entries:

            if items_added >= max_items:
                break

            if hasattr(entry,"published_parsed") and entry.published_parsed:

                utc_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))

                age_hours = (now - utc_time).total_seconds() / 3600

                if age_hours > max_age:
                    continue

                articles.append((utc_time, entry))
                items_added += 1

    if len(articles) == 0:
        continue

    # Sort newest first
    articles.sort(reverse=True, key=lambda x: x[0])

    html += f"<h2 style='margin-top:30px'>{category}</h2>"

    for utc_time, entry in articles:

        formatted_time, age = format_age(utc_time)

        publisher = entry.source.title if hasattr(entry,"source") else "Unknown Source"

        card_color = random.choice(card_colors)
        headline_color = random.choice(headline_colors)

        html += f"""
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
        {publisher} • {formatted_time} • {age}
        </span>

        </div>
        """

        count += 1

# ======================================
# EMAIL FOOTER
# ======================================

html += """
<hr>
<p style="font-size:12px;color:gray;text-align:center">
Generated from RSS feeds
</p>
</div>
</body>
</html>
"""

# ======================================
# EMAIL SEND
# ======================================

sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "📰 Daily Intelligence Brief"

msg.attach(MIMEText(html,"html"))

with smtplib.SMTP("smtp.gmail.com",587) as server:
    server.starttls()
    server.login(sender_email,app_password)
    server.sendmail(sender_email,receiver_email,msg.as_string())

print("Email sent successfully.")
