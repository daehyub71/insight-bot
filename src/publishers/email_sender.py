import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import List
from src.state import Article

class EmailSender:
    def __init__(self, template_dir: str = "templates"):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").replace("\xa0", "").replace(" ", "").strip()
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", "").strip() # Can be a comma-separated string
        
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def send_email(self, articles: List[Article]):
        if not self.smtp_user or not self.smtp_password or not self.recipient_email:
            print("⚠️ Email credentials not set. Skipping email.")
            return

        template = self.env.get_template("email_template.html")
        html_content = template.render(
            articles=articles,
            date=datetime.now().strftime("%Y-%m-%d")
        )

        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = self.recipient_email
        msg["Subject"] = Header(f"🧠 InsightBot Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}", 'utf-8')
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                recipients = [r.strip() for r in self.recipient_email.split(",")]
                server.sendmail(self.smtp_user, recipients, msg.as_string())
            print(f"📧 Email sent to {self.recipient_email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            raise e
