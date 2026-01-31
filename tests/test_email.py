import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.publishers.email_sender import EmailSender
from src.state import Article

def test_email():
    load_dotenv()
    print("📧 Testing Email Sender...")
    
    sender = EmailSender()
    
    # Check credentials
    if not sender.smtp_user or not sender.smtp_password:
        print("❌ SMTP credentials missing in .env")
        return

    # Create dummy article
    dummy_article = Article(
        source="test",
        title="[Test] InsightBot Email Verification",
        url="https://github.com/daehyub71/insight-bot",
        content="This is a test email to verify SMTP settings.",
        author="InsightBot Tester",
        date=str(datetime.now()),
        category="Test",
        relevance_score=1.0,
        summary="This is a summary of the test article.\nIt confirms that your email configuration is correct.",
        insight="Email system is operational."
    )

    print(f"Sending test email to: {sender.recipient_email}...")
    try:
        sender.send_email([dummy_article])
        print("✅ Email sent successfully! Please check your inbox.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    test_email()
