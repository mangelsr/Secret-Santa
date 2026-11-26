from unittest.mock import MagicMock, patch
from app.services.email_service import EmailService
from app.core.config import settings

def test_email_service_smtp():
    service = EmailService()
    
    with patch("app.services.email_service.settings") as mock_settings, \
         patch("smtplib.SMTP") as mock_smtp:
        mock_settings.SMTP_USER = "test@gmail.com"
        mock_settings.SMTP_PASSWORD = "secretapppassword"
        mock_settings.SMTP_HOST = "smtp.gmail.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_FROM_NAME = "Santa Secreto 🎅"
        
        mock_server_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        success = service.send_secret_santa_notification(
            giver_email="participant@gmail.com",
            giver_name="Juan",
            receiver_name="Maria",
            group_name="Familia 2026"
        )
        
        assert success is True
        mock_server_instance.login.assert_called_once_with("test@gmail.com", "secretapppassword")
        assert mock_server_instance.sendmail.called

def test_email_service_ses_fallback():
    service = EmailService()
    
    with patch("app.services.email_service.settings") as mock_settings:
        mock_settings.SMTP_USER = ""
        mock_settings.SMTP_PASSWORD = ""
        mock_settings.SES_SENDER_EMAIL = "notifications@test.com"
        
        service._ses_client = MagicMock()
        service._ses_client.send_email.return_value = {"MessageId": "12345"}
        
        success = service.send_secret_santa_notification(
            giver_email="participant@gmail.com",
            giver_name="Juan",
            receiver_name="Maria",
            group_name="Familia 2026"
        )
        
        assert success is True
        service._ses_client.send_email.assert_called_once()


def test_email_service_escapes_html_and_sanitizes_subject():
    service = EmailService()

    with patch("app.services.email_service.settings") as mock_settings:
        mock_settings.SMTP_USER = ""
        mock_settings.SMTP_PASSWORD = ""
        mock_settings.SES_SENDER_EMAIL = "notifications@test.com"

        service._ses_client = MagicMock()
        service._ses_client.send_email.return_value = {"MessageId": "abc"}

        success = service.send_secret_santa_notification(
            giver_email="participant@gmail.com",
            giver_name="<script>alert(1)</script>",
            receiver_name="Maria & <Bob>",
            group_name="Grupo\r\nBcc:evil@x.com",
        )

        assert success is True
        call_kwargs = service._ses_client.send_email.call_args.kwargs
        subject = call_kwargs["Message"]["Subject"]["Data"]
        html_body = call_kwargs["Message"]["Body"]["Html"]["Data"]

        assert "\r" not in subject and "\n" not in subject
        assert "<script>" not in html_body
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_body
        assert "Maria &amp; &lt;Bob&gt;" in html_body

