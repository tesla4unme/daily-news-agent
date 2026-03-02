import feedparser
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --------- RSS SOURCES ---------
barakar_url = "https://news.google.com/rss/search?q=Barakar"
ranchi_url = "https://news.google.com/rss/search?q=Ranchi"
india_url = "https://news.google.com/rss/search?q=breaking+news+india"

barakar_feed = feedparser.parse(barakar_url)
ranchi_feed = feedparser.parse(ranchi_url)
india_feed = feedparser.parse(india_url)

# --------- BUILD HTML EMAIL CONTENT ---------

today_date = datetime.now().strftime("%d %B %Y")

html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
<div style="max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 8px;">

<h1 style="text-align:center;">📰 Daily Intelligence Brief</h1>
<p style="text-align:center; color: gray;">{today_date}</p>

<hr>

<h2>🚨 Priority Local News (Barakar / Ranchi)</h2>
"""

local_count = 0

for entry in barakar_feed.entries[:3]:
    html_content += f"""
    <p><b>[Barakar]</b><br>
    <a href="{entry.link}" style="text-decoration:none; color:#1a73e8;">
    {entry.title}</a></p>
    """
    local_count += 1

for entry in ranchi_feed.entries[:3]:
    html_content += f"""
    <p><b>[Ranchi]</b><br>
    <a href="{entry.link}" style="text-decoration:none; color:#1a73e8;">
    {entry.title}</a></p>
    """
    local_count += 1

if local_count == 0:
    html_content += "<p style='color:gray;'>No local updates today.</p>"

html_content += """
<hr>
<h2>🌍 India General News</h2>
"""

for entry in india_feed.entries[:5]:
    html_content += f"""
    <p>
    <a href="{entry.link}" style="text-decoration:none; color:#1a73e8;">
    {entry.title}</a></p>
    """

html_content += """
<hr>
<p style="font-size:12px; color:gray; text-align:center;">
Automated News System • Powered by GitHub Actions
</p>

</div>
</body>
</html>
"""

# --------- EMAIL CONFIG ---------

sender_email = os.environ["SENDER_EMAIL"]
receiver_email = os.environ["RECEIVER_EMAIL"]
app_password = os.environ["APP_PASSWORD"]

subject = "Daily Intelligence Brief"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

msg.attach(MIMEText(html_content, "html"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully!")
