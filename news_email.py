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

# --------- BUILD HTML EMAIL CONTENT ---------
html_content = """
<html>
<body style="font-family: Arial, sans-serif;">
<h2>🚨 Priority Local News (Barakar / Ranchi)</h2>
"""
