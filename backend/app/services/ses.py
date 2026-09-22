from app.services.email_service import email_service, EmailService

# Maintain backward compatibility for any existing imports
ses_service = email_service
SESService = EmailService
