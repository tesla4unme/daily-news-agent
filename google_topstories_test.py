import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# -------- SETTINGS --------
RSS_URL = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

# -------- FETCH FEED --------
feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("No news items found.")
    exit()

# -------- BUILD HTML EMAIL --------
today_date = datetime.now().strftime("%d %B %Y")

html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
<div style="max-width: 750px; margin: auto; background: white; padding: 20px; border-radius: 8px;">

<h1 style="text-align:center;">📰 Google News – India Top Stories</h1>
<p style="text-align:center; color: gray;">{today_date}</p>
<hr>
"""

for entry in feed.entries:
    html_content += f"""
    <p>
    <a href="{entry.link}" style="text-decoration:none; color:#1a73e8;">
    {entry.title}</a>
    </p>
    """

html_content += """
<hr>
<p style="font-size:12px; color:gray; text-align:center;">
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

subject = "📰 Google India – All Top Stories"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

msg.attach(MIMEText(html_content, "html"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Google Top Stories email sent successfully.")
