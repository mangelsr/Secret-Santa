import boto3
from typing import Dict, Any
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
        Envía un correo individual mediante AWS SES informando quién es el amigo secreto asignado.
        """
        subject = f"🎄 ¡Tu Amigo Secreto en '{group_name}' ha sido asignado! 🎁"
        
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
                    <h1>🎅 Santa Secreto Navideño 🎁</h1>
                </div>
                <div class="content">
                    <h2>¡Hola {giver_name}!</h2>
                    <p>El grupo <strong>{group_name}</strong> ha cerrado su registro y el sorteo oficial se ha realizado con éxito.</p>
                    
                    <div class="card">
                        <p style="margin:0; font-size:16px; color:#4a5568;">Te ha tocado darle regalo a:</p>
                        <div class="target-name">✨ {receiver_name} ✨</div>
                    </div>
                    
                    <p style="color: #718096; font-size: 14px;">Recuerda mantener el secreto hasta el día de la entrega de regalos. ¡Felices Fiestas!</p>
                </div>
                <div class="footer">
                    Organizado con Santa Secreto App • Navidades en Familia 🎄
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
            print(f"Error al enviar correo a {giver_email} vía SES: {str(e)}")
            return False

ses_service = SESService()
