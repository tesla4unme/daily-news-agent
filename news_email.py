import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Fetch news
url = "https://news.google.com/rss/search?q=breaking+news+india"
feed = feedparser.parse(url)

news_content = ""

for i, entry in enumerate(feed.entries[:5]):
    news_content += f"{i+1}. {entry.title}\n{entry.link}\n\n"

# Email credentials from GitHub Secrets
sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "Daily Breaking News"

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
