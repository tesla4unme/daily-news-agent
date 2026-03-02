import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --------- RSS SOURCES ---------
barakar_url = "https://news.google.com/rss/search?q=Barakar"
ranchi_url = "https://news.google.com/rss/search?q=Ranchi"
india_url = "https://news.google.com/rss/search?q=breaking+news+india"

barakar_feed = feedparser.parse(barakar_url)
ranchi_feed = feedparser.parse(ranchi_url)
india_feed = feedparser.parse(india_url)

# --------- BUILD EMAIL CONTENT ---------
news_content = ""

# 🚨 PRIORITY LOCAL NEWS
news_content += "🚨 PRIORITY LOCAL NEWS (Barakar / Ranchi)\n\n"

local_count = 0

for entry in barakar_feed.entries[:3]:
    news_content += f"[Barakar] {entry.title}\n{entry.link}\n\n"
    local_count += 1

for entry in ranchi_feed.entries[:3]:
    news_content += f"[Ranchi] {entry.title}\n{entry.link}\n\n"
    local_count += 1

if local_count == 0:
    news_content += "No local updates today.\n\n"

# 🌍 INDIA NEWS
news_content += "\n🌍 INDIA GENERAL NEWS\n\n"

for entry in india_feed.entries[:5]:
    news_content += f"{entry.title}\n{entry.link}\n\n"

# --------- EMAIL CONFIG ---------
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "Daily Intelligence Brief"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

msg.attach(MIMEText(news_content, "plain"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully!")
