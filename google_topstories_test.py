import feedparser
import smtplib
import os
import pandas as pd  # Added for CSV handling
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time
import random

def titles_are_similar(t1, t2):
    # 1. Define common words to ignore (lowercase)
    stop_words = {'a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'is', 'with', 'from'}

    # 2. Clean and split into sets
    # We remove punctuation so "Toronto:" becomes "toronto"
    words1 = set(t1.lower().split())
    words2 = set(t2.lower().split()) # Basic split for the second one

    # 3. Remove the stop words from both sets
    important_words1 = words1 - stop_words
    important_words2 = words2 - stop_words

    # 4. Compare only the "important" words
    common = important_words1.intersection(important_words2)
    
    return len(common) >= 3

# ======================================
# GITA LINK PICKER (TEXT FILE VERSION)
# ======================================
def get_gita_link(file_path, repeat_days=3, offset=-30):
    try:
        with open(file_path, 'r') as f:
            links = [line.strip() for line in f if line.strip()]

        if not links:
            print("Gita file is empty")
            return None, None

        # Get day of year (1–365)
        day_number = datetime.now().timetuple().tm_yday

        # 🔥 Updated logic with offset control
        index = ((day_number // repeat_days) + offset) % len(links)

        # url = links[index]
        line = links[index]
        url, title = line.split(" ", 1)
        
        
        title = title + "<br>" + "🕉 Bhagavad Gita – Daily Wisdom"

        
        # title = "🕉 Bhagavad Gita – Daily Wisdom"

        print(f"Gita index: {index}, Offset: {offset}, URL: {url}")

        return title.strip(), url.strip()

    except Exception as e:
        print(f"Gita file error: {e}")
        return None, None
# ======================================
# ======================================
# --- READING ROOM CONFIGURATION ---
# ======================================
# The Raw link to your PDF
RAW_PDF_URL = "https://raw.githubusercontent.com/tesla4unme/daily-news-agent/main/01042026-md-red.pdf"

# This uses the Mozilla PDF.js viewer which does NOT have the 25MB limit.
# It is the most reliable way for large files on mobile.
MAGAZINE_URL = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={RAW_PDF_URL}"

MAGAZINE_TITLE = "Reader's Digest - April"

# --- HTML SECTION FOR EMAIL ---
magazine_html = f"""
<div style="margin: 20px 0; text-align: center;">
    <div style="
        display: inline-block; 
        background: linear-gradient(135deg, #2c3e50, #34495e); 
        color: white; 
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.15); 
        max-width: 90%;
        text-align: left;
    ">
        <h3 style="margin-top: 0; color: #ffffff; font-size: 20px;">📖 Daily Reading Room</h3>
        <p style="color: #ffffff; font-size: 15px; opacity: 0.9; line-height: 1.4;">
            Your 100-page challenge is waiting. This viewer is optimized for your large file.
        </p>
        <div style="text-align: center; margin-top: 15px;">
            <a href="{MAGAZINE_URL}" target="_blank"
               style="background-color: white; color: #2c3e50; padding: 12px 25px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                ✨ Open Magazine
            </a>
        </div>
    </div>
</div>
<hr style="border: 0; border-top: 1px solid #eee; margin: 25px 0;">
"""
# ======================================



# CONFIGURATION
# ======================================
# ======================================
# HCM LINK PICKER (TEXT FILE VERSION)
# ======================================
def get_HCM_link(file_path, repeat_days=3, offset=-30):
    try:
        with open(file_path, 'r') as f:
            links = [line.strip() for line in f if line.strip()]

        if not links:
            print("HCM file is empty")
            return None, None

        # Get day of year (1–365)
        day_number = datetime.now().timetuple().tm_yday

        # 🔥 Updated logic with offset control
        index = ((day_number // repeat_days) + offset) % len(links)

        # url = links[index]
        line = links[index]
        url, title = line.split(" ", 1)
        
        
        title = title + "<br>" + "🕉 HCM – Daily Learn"

        
        # title = "🕉 Bhagavad Gita – Daily Wisdom"

        print(f"HCM index: {index}, Offset: {offset}, URL: {url}")

        return title.strip(), url.strip()

    except Exception as e:
        print(f"HCM file error: {e}")
        return None, None
# ======================================
# CONFIGURATION
# ======================================
CATEGORIES = {
    "🍁 Toronto": {
        "feeds": [

            {
                "name": "Toronto-nowtoronto",
                "url": "https://nowtoronto.com/feed/",
                "max_age_hours": 24,
                "max_items": 5
            },

            {
                "name": "Toronto-Google.com",
                "url": "https://news.google.com/rss/search?q=Toronto&hl=en-CA&gl=CA&ceid=CA:en",
                "max_age_hours": 24,
                "max_items": 1
            }

        ]
    },
    "🛕 India": {
        "feeds": [

            {
                "name": "National-TheHindu",
                "url": "https://www.thehindu.com/news/national/feeder/default.rss",
                "max_age_hours": 24,
                "max_items": 4
            },

            {
                "name": "National-TimesofIndia",
                "url": "http://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
                "max_age_hours": 24,
                "max_items": 5
            },

            {
                "name": "National-Google.com",
                "url": "https://news.google.com/rss/search?q=India&hl=en-IN&gl=IN&ceid=IN:en",
                "max_age_hours": 24,
                "max_items": 5
            }

        ]
    },

    "🌆 Bengaluru": {
    "feeds": [
        {
            "name": "Bengaluru-Google",
            "url": "https://news.google.com/rss/search?q=Bengaluru&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 5
        }
    ]
},

"🌆 Asansol": {
    "feeds": [
        {
            "name": "Asansol-Google",
            "url": "https://news.google.com/rss/search?q=Asansol&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 1
        }
    ]
},

"🌆 Kolkata": {
    "feeds": [
        {
            "name": "Kolkata-Google",
            "url": "https://news.google.com/rss/search?q=Kolkata&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 1
        }
    ]
},

"🌆 Ranchi": {
    "feeds": [
        {
            "name": "Ranchi-Google",
            "url": "https://news.google.com/rss/search?q=Ranchi&hl=en-IN&gl=IN&ceid=IN:en",
            "max_age_hours": 24,
            "max_items": 1
        }
    ]
},
        

    "📰 Editorial": {
        "feeds": [

            {
                "name": "Opinion-TheHindu",
                "url": "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
                "max_age_hours": 24,
                "max_items": 3
            },

            {
                "name": "Blog-TimesofIndia",
                "url": "http://blogs.timesofindia.indiatimes.com/feed/defaultrss",
                "max_age_hours": 24,
                "max_items": 4
            },
            
            {
                "name": "Opinion-TheStatesman",
                "url": "https://www.thestatesman.com/rss/opinion",
                "max_age_hours": 24,
                "max_items": 2
            },
            
            
            {
                "name": "Opinion-Indianexpress",
                "url": "	https://indianexpress.com/section/opinion/feed/",
                "max_age_hours": 24,
                "max_items": 2
            }


        ]
    },

    "💻 Technology": {
        "feeds": [

            {
                "name": "Tech-TimesofIndia",
                "url": "https://timesofindia.indiatimes.com/technology/tech-news/rssfeeds/66949542.cms",
                "max_age_hours": 24,
                "max_items": 4
            },

            {
                "name": "AI-Google",
                "url": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en",
                "max_age_hours": 24,
                "max_items": 0
            },

            {
                "name": "Tech-BBC",
                "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
                "max_age_hours": 24,
                "max_items": 0
            },
            {
                "name": "AI-Indianexpress",
                "url": "https://indianexpress.com/section/technology/artificial-intelligence/feed/",
                "max_age_hours": 24,
                "max_items": 4
            }

        ]
    },

    "📈 Markets": {
        "feeds": [

            {
                "name": "Business-TimesofIndia",
                "url": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
                "max_age_hours": 24,
                "max_items": 0
            }

        ]
    }

}

# ======================================
# CATEGORY ANCHORS
# ======================================

CATEGORY_IDS = {
"🍁 Toronto": "toronto",
"🛕 India": "india",
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

<a href="#gita">🕉 Gita</a> |
<a href="#HCM">🕉 HCM</a> |
<a href="#toronto">🍁 Toronto</a> |
<a href="#india">🛕 India</a> |
<a href="#cities">🌆 Cities</a> |
<a href="#editorial">📰 Editorial</a> |
<a href="#technology">💻 Technology</a> |
<a href="#markets">📈 Markets</a>

</div>

<hr>
"""

# ======================================
# ADD GITA SECTION (NEW)
# ======================================
gita_title, gita_url = get_gita_link('gitaslokas.txt', repeat_days=3, offset=-30)

if gita_title:
    html += f"""
    <h2 id="gita" style="margin-top:30px; color:#ef6c00">🕉 Bhagavad Gita</h2>
    <div style="
        background:#fffbea;
        padding:15px;
        margin-bottom:12px;
        border-radius:8px;
        border:1px solid #ffe082;
        border-left:4px solid #ef6c00;
    ">
        <b><a href="{gita_url}" style="text-decoration:none; color:#1a73e8; font-size:18px;">
            {gita_title}
        </a></b>
        <p style="margin:10px 0 0 0; font-size:12px; color:#666;">
            Refreshing every few days based on your schedule.
        </p>
    </div>
    <hr>
    """

count = 1
# ======================================
# ADD HCM SECTION (NEW)
# ======================================
HCM_title, HCM_url = get_HCM_link('HCM.txt', repeat_days=3, offset=-30)

if HCM_title:
    html += f"""
    <h2 id="HCM" style="margin-top:30px; color:#ef6c00">🕉 HCM</h2>
    <div style="
        background:#fffbea;
        padding:15px;
        margin-bottom:12px;
        border-radius:8px;
        border:1px solid #ffe082;
        border-left:4px solid #ef6c00;
    ">
        <b><a href="{HCM_url}" style="text-decoration:none; color:#1a73e8; font-size:18px;">
            {HCM_title}
        </a></b>
        <p style="margin:10px 0 0 0; font-size:12px; color:#666;">
            Refreshing every few days based on your schedule.
        </p>
    </div>
    <hr>
    """

count = 1


# ======================================
# ADD MAGAZINE SECTION (NEW FIX HERE)
# ======================================
html += magazine_html  # <--- THIS LINE WAS MISSING
# ======================================


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
    title_store = ""
    for utc_time, entry, feed_name in articles:
        if titles_are_similar(entry.title, title_store):
            continue  # Skip if 3 words match the previous title
            
        title_store = entry.title

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
