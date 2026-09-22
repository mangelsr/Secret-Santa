import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import boto3

from app.core.config import settings

class EmailService:
    def __init__(self):
        self._ses_client = None

    @property
    def ses_client(self):
        if self._ses_client is None:
            self._ses_client = boto3.client('ses', region_name=settings.AWS_REGION)
        return self._ses_client

    def send_secret_santa_notification(
        self, 
        giver_email: str, 
        giver_name: str, 
        receiver_name: str, 
        group_name: str
    ) -> bool:
        """
        Sends an individual email revealing the assigned Secret Santa target.
        Prefers SMTP (Gmail) if SMTP_USER and SMTP_PASSWORD are configured, 
        otherwise falls back to AWS SES.
        """
        subject = f"🎄 ¡Tu amigo secreto para '{group_name}' ha sido asignado! 🎁"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f7; color: #333; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 2px solid #e53e3e; }}
                .header {{ background: linear-gradient(135deg, #c53030 0%, #9b2c2c 100%); padding: 30px 20px; text-align: center; color: white; }}
                .header h1 {{ margin: 0; font-size: 26px; letter-spacing: 1px; }}
                .content {{ padding: 30px 20px; text-align: center; }}
                .card {{ background: #fff5f5; border: 2px dashed #e53e3e; border-radius: 10px; padding: 25px; margin: 20px 0; }}
                .target-name {{ font-size: 32px; font-weight: bold; color: #c53030; margin: 10px 0; }}
                .footer {{ background: #edf2f7; padding: 15px; text-align: center; font-size: 13px; color: #718096; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎅 Amigo Secreto Navideño 🎁</h1>
                </div>
                <div class="content">
                    <h2>¡Hola {giver_name}!</h2>
                    <p>El grupo <strong>{group_name}</strong> ha cerrado inscripciones y el sorteo oficial se ha realizado con éxito.</p>
                    
                    <div class="card">
                        <p style="margin:0; font-size:16px; color:#4a5568;">Te tocó regalarle a:</p>
                        <div class="target-name">✨ {receiver_name} ✨</div>
                    </div>
                    
                    <p style="color: #718096; font-size: 14px;">¡Recuerda mantenerlo en secreto hasta el día de la entrega de regalos! ¡Felices Fiestas! 🎄</p>
                </div>
                <div class="footer">
                    Organizado con la App de Santa Secreto • Navidad en Familia 🎄
                </div>
            </div>
        </body>
        </html>
        """
        
        # Check if SMTP is configured
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            return self._send_via_smtp(giver_email, subject, html_body)
        else:
            return self._send_via_ses(giver_email, subject, html_body)

    def _send_via_smtp(self, to_email: str, subject: str, html_body: str) -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_USER))
            msg['To'] = to_email
            
            part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part)
            
            # Gmail App Password often works on port 587 (STARTTLS) or port 465 (SSL)
            if settings.SMTP_PORT == 465:
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
                    
            print(f"Successfully sent email to {to_email} via SMTP ({settings.SMTP_HOST})")
            return True
        except Exception as e:
            print(f"Error sending email to {to_email} via SMTP: {str(e)}")
            return False

    def _send_via_ses(self, to_email: str, subject: str, html_body: str) -> bool:
        try:
            self.ses_client.send_email(
                Source=settings.SES_SENDER_EMAIL,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
                }
            )
            print(f"Successfully sent email to {to_email} via AWS SES")
            return True
        except Exception as e:
            print(f"Error sending email to {to_email} via SES: {str(e)}")
            return False

email_service = EmailService()
