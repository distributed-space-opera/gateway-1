import smtplib
import os
from email.mime.text import MIMEText

# EMAIL = os.environ.get("EMAIL")
# PASSWORD = os.environ.get("PASSWORD")
EMAIL = "iam191911918114@gmail.com"
PASSWORD = "sfubvzmprlzsxbny"
RECEIVER = "saikiran.madupu@gmail.com"

html = open("receipt.html")
msg = MIMEText(html.read(), "html")
msg["Subject"] = "hello"
msg["From"] = EMAIL
msg["To"] = RECEIVER

debug = False

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL, PASSWORD)
text = msg.as_string()
server.sendmail(EMAIL, RECEIVER, text)
server.quit()