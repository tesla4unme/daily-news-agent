# --------- BUILD HTML EMAIL CONTENT ---------
html_content = """
<html>
<body style="font-family: Arial, sans-serif;">

<h2>🚨 Priority Local News (Barakar / Ranchi)</h2>
"""

local_count = 0

for entry in barakar_feed.entries[:3]:
    html_content += f"""
    <p><b>[Barakar]</b> 
    <a href="{entry.link}">{entry.title}</a></p>
    """
    local_count += 1

for entry in ranchi_feed.entries[:3]:
    html_content += f"""
    <p><b>[Ranchi]</b> 
    <a href="{entry.link}">{entry.title}</a></p>
    """
    local_count += 1

if local_count == 0:
    html_content += "<p>No local updates today.</p>"

html_content += """
<hr>
<h2>🌍 India General News</h2>
"""

for entry in india_feed.entries[:5]:
    html_content += f"""
    <p><a href="{entry.link}">{entry.title}</a></p>
    """

html_content += """
</body>
</html>
"""
