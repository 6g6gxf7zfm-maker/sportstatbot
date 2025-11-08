"""Email notification system for digest completion and errors."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Email notification system.

    Features:
    - Digest completion notifications
    - Error alerts
    - Daily/weekly summaries
    - HTML and plain text emails
    - Multiple recipients
    """

    def __init__(
        self,
        smtp_host: str = 'smtp.gmail.com',
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """
        Initialize email notifier.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            from_email: Sender email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username or os.getenv('SMTP_USERNAME')
        self.password = password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('SMTP_FROM_EMAIL', self.username)

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send an email.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body_text: Plain text email body
            body_html: HTML email body (optional)

        Returns:
            True if successful
        """
        if not self.username or not self.password:
            logger.error("SMTP credentials not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)

            # Add plain text part
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)

            # Add HTML part if provided
            if body_html:
                part2 = MIMEText(body_html, 'html')
                msg.attach(part2)

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {len(to_emails)} recipients: {subject}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_digest_ready_notification(
        self,
        to_emails: List[str],
        sport: str,
        digest_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Send notification that a digest is ready.

        Args:
            to_emails: List of recipient email addresses
            sport: Sport name
            digest_url: URL to the digest
            metadata: Additional metadata

        Returns:
            True if successful
        """
        metadata = metadata or {}
        date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))

        subject = f"🏆 {sport.upper()} Digest Ready - {date}"

        body_text = f"""
Your {sport.upper()} digest for {date} is ready!

"""
        if digest_url:
            body_text += f"View digest: {digest_url}\n\n"

        if metadata:
            body_text += "Details:\n"
            for key, value in metadata.items():
                body_text += f"  {key}: {value}\n"

        body_text += f"\n---\nSportStatBot\nGenerated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body_html = f"""
<html>
  <body>
    <h2>🏆 Your {sport.upper()} Digest is Ready!</h2>
    <p>Date: <strong>{date}</strong></p>
"""

        if digest_url:
            body_html += f'    <p><a href="{digest_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Digest</a></p>\n'

        if metadata:
            body_html += '    <h3>Details:</h3>\n    <ul>\n'
            for key, value in metadata.items():
                body_html += f'      <li><strong>{key}:</strong> {value}</li>\n'
            body_html += '    </ul>\n'

        body_html += f"""
    <hr>
    <p style="color: #666; font-size: 12px;">
      SportStatBot<br>
      Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
  </body>
</html>
"""

        return self.send_email(to_emails, subject, body_text, body_html)

    def send_error_notification(
        self,
        to_emails: List[str],
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ) -> bool:
        """
        Send error notification.

        Args:
            to_emails: List of recipient email addresses
            error_type: Type of error
            error_message: Error message
            context: Additional context information

        Returns:
            True if successful
        """
        subject = f"⚠️ SportStatBot Error: {error_type}"

        body_text = f"""
An error occurred in SportStatBot:

Error Type: {error_type}
Error Message: {error_message}

"""

        if context:
            body_text += "Context:\n"
            for key, value in context.items():
                body_text += f"  {key}: {value}\n"

        body_text += f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body_html = f"""
<html>
  <body>
    <h2 style="color: #d32f2f;">⚠️ SportStatBot Error</h2>
    <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f;">
      <p><strong>Error Type:</strong> {error_type}</p>
      <p><strong>Error Message:</strong> {error_message}</p>
    </div>
"""

        if context:
            body_html += '    <h3>Context:</h3>\n    <ul>\n'
            for key, value in context.items():
                body_html += f'      <li><strong>{key}:</strong> {value}</li>\n'
            body_html += '    </ul>\n'

        body_html += f"""
    <p style="color: #666; font-size: 12px;">
      Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
  </body>
</html>
"""

        return self.send_email(to_emails, subject, body_text, body_html)

    def send_daily_summary(
        self,
        to_emails: List[str],
        statistics: Dict
    ) -> bool:
        """
        Send daily summary with statistics.

        Args:
            to_emails: List of recipient email addresses
            statistics: Dictionary with statistics

        Returns:
            True if successful
        """
        date = datetime.now().strftime('%Y-%m-%d')
        subject = f"📊 SportStatBot Daily Summary - {date}"

        total_digests = statistics.get('total_digests', 0)
        successful = statistics.get('successful', 0)
        failed = statistics.get('failed', 0)
        sports = statistics.get('sports', [])

        body_text = f"""
Daily Summary for {date}

Total Digests: {total_digests}
Successful: {successful}
Failed: {failed}

Sports Covered:
"""

        for sport, count in sports:
            body_text += f"  - {sport.upper()}: {count} digest(s)\n"

        body_text += f"\n---\nSportStatBot Daily Summary"

        body_html = f"""
<html>
  <body>
    <h2>📊 Daily Summary</h2>
    <p>Date: <strong>{date}</strong></p>

    <table style="border-collapse: collapse; margin: 20px 0;">
      <tr style="background-color: #f5f5f5;">
        <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Metric</th>
        <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Value</th>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;">Total Digests</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">{total_digests}</td>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;">Successful</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #4caf50;">{successful}</td>
      </tr>
      <tr>
        <td style="padding: 10px; border: 1px solid #ddd;">Failed</td>
        <td style="padding: 10px; border: 1px solid #ddd; text-align: right; color: #d32f2f;">{failed}</td>
      </tr>
    </table>

    <h3>Sports Covered:</h3>
    <ul>
"""

        for sport, count in sports:
            body_html += f"      <li><strong>{sport.upper()}:</strong> {count} digest(s)</li>\n"

        body_html += """
    </ul>

    <hr>
    <p style="color: #666; font-size: 12px;">SportStatBot Daily Summary</p>
  </body>
</html>
"""

        return self.send_email(to_emails, subject, body_text, body_html)
