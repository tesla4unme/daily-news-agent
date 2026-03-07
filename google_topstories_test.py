import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
import time
import random

# -------- SETTINGS --------
RSS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

city_feeds = {
    "🌆 Bengaluru": "https://news.google.com/rss/search?q=Bengaluru&hl=en-IN&gl=IN&ceid=IN:en",  
    "🧬 AI"    : "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en"
}

headline_colors = [
"#1a73e8","#c62828","#2e7d32","#6a1b9a",
"#ef6c00","#00838f","#5d4037","#455a64"
]

card_colors = [
"#fdf2f2","#f2f7fd","#f4fbf4","#faf3fd",
"#fff6ed","#f0fafa","#f7f7f7","#fffbea"
]

# -------- FETCH MAIN FEED --------
feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("No news items found.")
    exit()

# -------- FILTER & SORT MAIN ARTICLES (LAST 2 HOURS) --------
articles = []
now_utc = datetime.now(timezone.utc)

for entry in feed.entries:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        # Convert to aware datetime
        utc_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)
    else:
        continue

    # -------- FILTER > 2 HOURS (7200 Seconds) --------
    if (now_utc - utc_time).total_seconds() > 7200:
        continue

    articles.append((utc_time, entry))

# Sort all main news by newest first
articles.sort(reverse=True, key=lambda x: x[0])

# -------- HEADER INFO --------
today_date = datetime.now().strftime("%d %B %Y")

# -------- BUILD EMAIL --------
html_content = f"""
<html>
<body style="font-family:Arial, sans-serif;background:#f4f6f8;padding:20px;">
<div style="max-width:760px;margin:auto;background:white;padding:25px;border-radius:12px;box-shadow:0 4px 14px rgba(0,0,0,0.08);">
<h1 style="text-align:center;margin-bottom:5px;">📰 News India</h1>
<p style="text-align:center;color:gray;">{today_date} • Last 2 Hours</p>
<hr>
"""

count = 1

# -------- CITY NEWS SECTIONS (KEEP ORIGINAL LOGIC) --------
for city, url in city_feeds.items():
    city_feed = feedparser.parse(url)
    if len(city_feed.entries) == 0:
        continue

    city_articles = []
    for entry in city_feed.entries:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            utc_time = datetime.fromtimestamp(time.mktime(entry.published_parsed), timezone.utc)
        else:
            continue
        
        # City feeds kept at 24h filter as per original logic
        if (now_utc - utc_time).total_seconds() > 86400:
            continue
        city_articles.append((utc_time, entry))

    city_articles.sort(reverse=True, key=lambda x: x[0])

    html_content += f"<h2 style='margin-top:35px;color:#333;'>{city}</h2>"

    for utc_time, entry in city_articles[:10]:
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        age = now_ist - ist_time
        hours, remainder = divmod(int(age.total_seconds()), 3600)
        minutes = remainder // 60
        age_label = f"{hours}h ago" if hours > 0 else f"{minutes}m ago"
        formatted_time = ist_time.strftime("%d %b %Y • %H:%M IST")
        publisher = entry.source.title if hasattr(entry,"source") else "Unknown Source"
        card_color = random.choice(card_colors)
        headline_color = random.choice(headline_colors)

        html_content += f"""
        <div style="background:{card_color};padding:15px;margin-bottom:12px;border-radius:8px;border:1px solid #e6e6e6;border-left:4px solid #1a73e8;">
        <b>{count}. <a href="{entry.link}" style="text-decoration:none;color:{headline_color};font-size:17px;line-height:1.35;">{entry.title}</a></b>
        <br><br>
        <span style="font-size:12px;color:#666;background:#eef2f7;padding:3px 7px;border-radius:4px;">{publisher} • {formatted_time} • {age_label}</span>
        </div>
        """
        count += 1

# -------- MAIN FEED SECTION (FLATTENED & RECENT) --------
if articles:
    html_content += "<h2 style='margin-top:35px;color:#333;'>🔥 Latest Breaking News</h2>"
    
    for utc_time, entry in articles:
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        now_ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        age = now_ist - ist_time
        minutes = int(age.total_seconds() // 60)
        age_label = f"{minutes}m ago"
        
        formatted_time = ist_time.strftime("%H:%M IST")
        publisher = entry.source.title if hasattr(entry,"source") else "Unknown Source"
        card_color = random.choice(card_colors)
        headline_color = random.choice(headline_colors)

        html_content += f"""
        <div style="background:{card_color};padding:15px;margin-bottom:12px;border-radius:8px;border:1px solid #e6e6e6;border-left:4px solid #d32f2f;">
        <b>{count}. <a href="{entry.link}" style="text-decoration:none;color:{headline_color};font-size:17px;line-height:1.35;">{entry.title}</a></b>
        <br><br>
        <span style="font-size:12px;color:#666;background:#fdeaea;padding:3px 7px;border-radius:4px;">{publisher} • {formatted_time} • {age_label}</span>
        </div>
        """
        count += 1

html_content += """
<hr>
<p style="font-size:12px;color:gray;text-align:center;">Source: Google News India RSS</p>
</div>
</body>
</html>
"""

# -------- EMAIL CONFIG --------
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = f"📰 News India Digest ({datetime.now().strftime('%H:%M')})"
msg.attach(MIMEText(html_content, "html"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print(f"Email sent successfully with {count-1} articles.")
