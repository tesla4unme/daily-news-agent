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

    "India": {
        "feeds": [

            {
                "name": "National-TheHindu",
                "url": "https://www.thehindu.com/news/national/feeder/default.rss",
                "max_age_hours": 24,
                "max_items": 10
            },

            {
                "name": "National-TimesofIndia",
                "url": "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
                "max_age_hours": 24,
                "max_items": 10
            },

            {
                "name": "National-Google.com",
                "url": "https://news.google.com/rss/search?q=India&hl=en-IN&gl=IN&ceid=IN:en",
                "max_age_hours": 24,
                "max_items": 15
            }

        ]
    },

    "🌆 Bengaluru": {
    "feeds": [
        {
            "name": "Bengaluru-Google",
            "url": "https://news.google.com/rss/search?q=Bengaluru&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 10
        }
    ]
},

"🌆 Asansol": {
    "feeds": [
        {
            "name": "Asansol-Google",
            "url": "https://news.google.com/rss/search?q=Asansol&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 10
        }
    ]
},

"🌆 Kolkata": {
    "feeds": [
        {
            "name": "Kolkata-Google",
            "url": "https://news.google.com/rss/search?q=Kolkata&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 10
        }
    ]
},

"🌆 Ranchi": {
    "feeds": [
        {
            "name": "Ranchi-Google",
            "url": "https://news.google.com/rss/search?q=Ranchi&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 10
        }
    ]
},
       

    "📰 Editorial": {
        "feeds": [

            {
                "name": "Opinion-TheHindu",
                "url": "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
                "max_age_hours": 24,
                "max_items": 10
            },

            {
                "name": "Blog-TimesofIndia",
                "url": "http://blogs.timesofindia.indiatimes.com/feed/defaultrss",
                "max_age_hours": 24,
                "max_items": 10
            }

        ]
    },

    "💻 Technology": {
        "feeds": [

            {
                "name": "Tech-TimesofIndia",
                "url": "https://timesofindia.indiatimes.com/technology/tech-news/rssfeeds/66949542.cms",
                "max_age_hours": 24,
                "max_items": 10
            },

            {
                "name": "AI-Google",
                "url": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en",
                "max_age_hours": 24,
                "max_items": 10
            },

            {
                "name": "Tech-BBC",
                "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
                "max_age_hours": 24,
                "max_items": 10
            }

        ]
    },

    "📈 Markets": {
        "feeds": [

            {
                "name": "Business-TimesofIndia",
                "url": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
                "max_age_hours": 24,
                "max_items": 10
            }

        ]
    }

}

# ======================================
# CATEGORY ANCHORS
# ======================================

CATEGORY_IDS = {
"India": "india",
"🌆 Cities": "cities",
"📰 Editorial": "editorial",
"💻 Technology": "technology",
"📈 Markets": "markets"
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
# TIME FORMAT
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
# EMAIL HEADER
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

<h1 style="text-align:center">📰 Divya Drishti</h1>
<p style="text-align:center;color:gray;">{today}</p>

<div style="text-align:center;margin:15px 0;font-size:14px">

<a href="#india">India</a> |
<a href="#cities">🌆 Cities</a> |
<a href="#editorial">📰 Editorial</a> |
<a href="#technology">💻 Technology</a> |
<a href="#markets">📈 Markets</a>

</div>

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
        feed_name = feed_cfg.get("name","")
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

                articles.append((utc_time, entry, feed_name))
                items_added += 1

    if len(articles) == 0:
        continue

    articles.sort(reverse=True, key=lambda x: x[0])

    category_id = CATEGORY_IDS.get(category,"section")

    html += f"<h2 id='{category_id}' style='margin-top:30px'>{category}</h2>"

    for utc_time, entry, feed_name in articles:

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
        {publisher} • {formatted_time} • {age} • 
        <span style="color:#ef6c00">{feed_name}</span>
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
# SEND EMAIL
# ======================================

sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "📰 Divya Drishti"

msg.attach(MIMEText(html,"html"))

with smtplib.SMTP("smtp.gmail.com",587) as server:
    server.starttls()
    server.login(sender_email,app_password)
    server.sendmail(sender_email,receiver_email,msg.as_string())

print("Email sent successfully.")
