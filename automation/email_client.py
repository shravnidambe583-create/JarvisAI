import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailClient:
    """Handles sending emails via SMTP, including emergency alerts."""
    
    def __init__(self):
        # Retrieve credentials from environment variables or use dummy configurations
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.email_address = os.environ.get("JARVIS_EMAIL_ADDRESS", "")
        self.email_password = os.environ.get("JARVIS_EMAIL_PASSWORD", "")
        
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Sends a standard email."""
        if not self.email_address or not self.email_password:
            print("[Email] Error: SMTP email credentials not configured in environment variables.")
            return False
            
        print(f"[Email] Sending email to {to_email}...")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Upgrade connection to secure
            server.login(self.email_address, self.email_password)
            
            # Send and close
            server.sendmail(self.email_address, to_email, msg.as_string())
            server.quit()
            print("[Email] Email sent successfully.")
            return True
        except Exception as e:
            print(f"[Email] SMTP error: {e}")
            return False

    def send_emergency_alert(self, contacts: list, location_details: str = "Unknown location") -> bool:
        """Sends an emergency panic email to a list of trusted contact emails."""
        if not contacts:
            print("[Email] Error: No emergency contacts provided.")
            return False
            
        from datetime import datetime
        subject = "🚨 EMERGENCY ALERT - JARVIS SYSTEM 🚨"
        body = f"""
This is an automated emergency message sent from the JARVIS X Desktop AI Assistant.

The user has triggered EMERGENCY MODE on their PC.
Location/Context Details: {location_details}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please contact or check on the user immediately.
        """
        
        all_success = True
        for contact in contacts:
            success = self.send_email(contact, subject, body)
            if not success:
                all_success = False
                
        return all_success
