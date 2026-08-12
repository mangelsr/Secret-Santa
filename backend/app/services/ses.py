import boto3
from app.core.config import settings

class SESService:
    def __init__(self):
        self.ses_client = boto3.client('ses', region_name=settings.AWS_REGION)

    def send_secret_santa_notification(
        self, 
        giver_email: str, 
        giver_name: str, 
        receiver_name: str, 
        group_name: str
    ) -> bool:
        """
        Sends an individual email via AWS SES revealing the assigned Secret Santa target.
        """
        subject = f"🎄 Your Secret Santa target for '{group_name}' has been assigned! 🎁"
        
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
                    <h1>🎅 Christmas Secret Santa 🎁</h1>
                </div>
                <div class="content">
                    <h2>Hello {giver_name}!</h2>
                    <p>The group <strong>{group_name}</strong> has finalized registration and the official draw has been performed successfully.</p>
                    
                    <div class="card">
                        <p style="margin:0; font-size:16px; color:#4a5568;">Your assigned Secret Santa recipient is:</p>
                        <div class="target-name">✨ {receiver_name} ✨</div>
                    </div>
                    
                    <p style="color: #718096; font-size: 14px;">Remember to keep it secret until gift exchange day. Happy Holidays!</p>
                </div>
                <div class="footer">
                    Organized with Secret Santa App • Family Christmas 🎄
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            self.ses_client.send_email(
                Source=settings.SES_SENDER_EMAIL,
                Destination={'ToAddresses': [giver_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
                }
            )
            return True
        except Exception as e:
            print(f"Error sending email to {giver_email} via SES: {str(e)}")
            return False

ses_service = SESService()
