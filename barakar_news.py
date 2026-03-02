import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import time

# -------- SETTINGS --------
RSS_URL = "https://news.google.com/rss/search?q=Barakar"
HOURS_BACK = 24

# -------- FETCH FEED --------
feed = feedparser.parse(RSS_URL)

now = datetime.utcnow()
cutoff_time = now - timedelta(hours=HOURS_BACK)

recent_articles = []

for entry in feed.entries:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        published_time = datetime.fromtimestamp(
            time.mktime(entry.published_parsed)
        )
        if published_time >= cutoff_time:
            recent_articles.append(entry)

# If no recent articles → exit silently
if len(recent_articles) == 0:
    print("No new Barakar news in last 24 hours. No email sent.")
    exit()

# -------- BUILD HTML EMAIL --------
today_date = datetime.now().strftime("%d %B %Y")

html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
<div style="max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 8px;">

<h1 style="text-align:center;">🚨 Barakar News Alert</h1>
<p style="text-align:center; color: gray;">{today_date}</p>
<hr>
"""

for entry in recent_articles:
    html_content += f"""
    <p>
    <a href="{entry.link}" style="text-decoration:none; color:#1a73e8;">
    {entry.title}</a>
    </p>
    """

html_content += """
<hr>
<p style="font-size:12px; color:gray; text-align:center;">
Regional Monitoring System • Barakar
</p>

</div>
</body>
</html>
"""

# -------- EMAIL CONFIG --------
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "🚨 Barakar News Update"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

msg.attach(MIMEText(html_content, "html"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Barakar news email sent successfully.")
